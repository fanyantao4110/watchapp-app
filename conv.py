import os, io, json, zipfile, struct, sys

# ---- 完全按 hap-sign-utils/index.html 的 parseBinHeader 实现 ----
SIGN_HEAD_MARKER = "hw signed app   1000"

def u32(b, o): return struct.unpack_from(">I", b, o)[0]
def u16(b, o): return struct.unpack_from(">H", b, o)[0]
def u64(b, o): return struct.unpack_from(">Q", b, o)[0]

def is_pro_head(b0, b1):
    return b0 == 0x02 or (b0 == 0x01 and b1 == 0x00)

def parse_bin(data):
    if len(data) < 10 or data[0] != 0xBE:
        raise ValueError("不是有效 .bin（魔数不匹配）")
    bn_len = u32(data, 1)
    bundle = data[5:5 + bn_len].decode("utf-8")

    signed = False
    unsigned_end = len(data)
    p7b = None

    if len(data) >= 32:
        tail = data[-32:-12].decode("utf-8", "ignore")
        if tail == SIGN_HEAD_MARKER:
            signed = True
            sub = u32(data, len(data) - 12)
            cands = [len(data) - sub, len(data) - sub - 8, len(data) - sub - 16, len(data) - sub + 8]
            for pos in cands:
                if pos < 10 or pos + 8 > len(data) - 32:
                    continue
                if not is_pro_head(data[pos], data[pos + 1]):
                    continue
                plen = u16(data, pos + 2)
                pstart = u32(data, pos + 4)
                if pstart == pos + 16 and pstart + plen <= len(data) - 32:
                    unsigned_end = pos
                    p7b = data[pstart:pstart + plen]
                    break
            if p7b is None:  # 兜底扫描
                for i in range(1, len(data) - 32 - 8):
                    if not is_pro_head(data[i], data[i + 1]):
                        continue
                    off = u32(data, i + 4)
                    if off == i + 16:
                        plen = u16(data, i + 2)
                        if off + plen <= len(data) - 32:
                            unsigned_end = i
                            p7b = data[off:off + plen]
                            break
            if p7b is None:
                raise ValueError("已签名但定位不到 proBlock")

    files = []
    pos = 5 + bn_len
    while pos < unsigned_end:
        if pos + 4 > unsigned_end:
            break
        nl = u32(data, pos)
        if nl == 0 or nl > 4096 or pos + 4 + nl > unsigned_end:
            break
        name = data[pos + 4:pos + 4 + nl].decode("utf-8")
        pos += 4 + nl
        if pos + 4 > unsigned_end:
            break
        pl = u32(data, pos)
        if pl > 4096 or pos + 4 + pl > unsigned_end:
            break
        rel = data[pos + 4:pos + 4 + pl].decode("utf-8")
        pos += 4 + pl
        if pos + 8 > unsigned_end:
            break
        cl = u64(data, pos)
        pos += 8
        if pos + cl > unsigned_end:
            break
        content = data[pos:pos + cl]
        pos += cl
        full = name if rel == "" else rel.lstrip("/") + "/" + name
        files.append((full, content))
    return bundle, files, signed, p7b

def build_zip(entries, comp=zipfile.ZIP_STORED):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", comp) as z:
        for name, data in entries:
            zi = zipfile.ZipInfo(name, date_time=(2026, 11, 19, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_STORED          # 与工具一致：STORE
            zi.external_attr = 0o644 << 16
            z.writestr(zi, data)
    return buf.getvalue()

src = {
    "2048新版_1.1_Fit2_ORDMPMNOPSLAFA64C43B94C091B.hap": "2048_fit2.app",
    "小恐龙坤坤重置版_1.0.0_Fit2_ORDMPMK357MC3C373B9D5B7F350.hap": "kongkong_fit2.app",
    "斗地主_1.0.0_Fit2_ORDMPMJVAVT0352DDCF07AF453F.hap": "doudizhu_fit2.app",
    "棋类游戏(五子,围,象棋)_2.0_Fit2_ORDMPMJW0G02F9867B225294F18.hap": "qilei_fit2.app",
    "跳一跳,螃蟹先生_2.1_Fit2_ORDMPMJYCY48D2ACC58AC57ADAE.hap": "tiaoyi_fit2.app",
}

os.makedirs("/root/hapwork/out", exist_ok=True)
meta = []
for fn, out in src.items():
    raw = open("/root/hapwork/" + fn, "rb").read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    binname = [n for n in z.namelist() if n.endswith(".bin")][0]
    binbuf = z.read(binname)
    bundle, files, signed, p7b = parse_bin(binbuf)

    # 1) 还原未签名 hap（zip 内为真实文件）
    hap = build_zip(files)
    # 2) 包成 app：zip 内 1 个 STORE 的 .hap，与工具的 buildAppFromHap 一致
    app = build_zip([("entry-release-lite.hap", hap)])
    open("/root/hapwork/out/" + out, "wb").write(app)

    info = {}
    for p, d in files:
        if p.endswith("pack.info"):
            try:
                pi = json.loads(d)
                info["pack_label"] = pi.get("summary", {}).get("app", {}).get("label")
                info["pack_bundle"] = pi.get("summary", {}).get("app", {}).get("bundleName")
                info["pack_ver"] = pi.get("summary", {}).get("app", {}).get("version")
                info["mods"] = [m.get("name") for m in pi.get("summary", {}).get("modules", [])]
            except Exception as e:
                info["pack_err"] = str(e)
        if p == "config.json":
            cfg = json.loads(d)
            info["cfg_bundle"] = cfg.get("app", {}).get("bundleName")
            info["cfg_ver"] = cfg.get("app", {}).get("versionName") or cfg.get("app", {}).get("version", {}).get("name")
            info["cfg_label"] = cfg.get("app", {}).get("label")
            info["minApi"] = cfg.get("app", {}).get("minAPIVersion")
            info["devices"] = cfg.get("module", {}).get("deviceTypes") or cfg.get("app", {}).get("deviceType")

    meta.append(dict(src=fn, out=out, bundle=bundle, signed=signed, p7b=len(p7b) if p7b else 0,
                     files=len(files), hap=len(hap), app=len(app), **info))
    print("=== ", fn[:30])
    print("   bin bundle:", bundle, "| signed:", signed, "| p7b:", len(p7b) if p7b else 0)
    print("   files:", len(files), "| hap:", len(hap), "| app:", len(app))
    print("   ", {k: v for k, v in info.items()})

json.dump(meta, open("/root/hapwork/out/meta.json", "w"), ensure_ascii=False, indent=1)
print("\n打包完成:", len(meta))
