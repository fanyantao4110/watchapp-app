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

