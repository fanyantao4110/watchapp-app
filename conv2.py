"""hap -> app 正式结构：zip{ pack.info , <package>.hap }

pack.info 从原 hap 内部原样取出（就是 app 级清单），
hap 条目名取 pack.info.packages[0].name + ".hap"（这里都是 entry-release-lite）。
"""
import os, io, json, zipfile, sys
sys.path.insert(0, '/root/hapwork')
from binlib import parse_bin, build_zip

SRC = {
    "2048新版_1.1_Fit2_ORDMPMNOPSLAFA64C43B94C091B.hap": "2048_fit2.app",
    "小恐龙坤坤重置版_1.0.0_Fit2_ORDMPMK357MC3C373B9D5B7F350.hap": "kongkong_fit2.app",
    "斗地主_1.0.0_Fit2_ORDMPMJVAVT0352DDCF07AF453F.hap": "doudizhu_fit2.app",
    "棋类游戏(五子,围,象棋)_2.0_Fit2_ORDMPMJW0G02F9867B225294F18.hap": "qilei_fit2.app",
    "跳一跳,螃蟹先生_2.1_Fit2_ORDMPMJYCY48D2ACC58AC57ADAE.hap": "tiaoyi_fit2.app",
}

out_dir = "/root/hapwork/out"
meta = []
for fn, out in SRC.items():
    raw = open("/root/hapwork/" + fn, "rb").read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    binname = [n for n in z.namelist() if n.endswith(".bin")][0]
    bundle, files, signed, p7b = parse_bin(z.read(binname))

    packinfo = None
    for p, d in files:
        if p.endswith("pack.info"):
            packinfo = d
            break
    if packinfo is None:
        raise SystemExit("缺 pack.info: " + fn)
    pi = json.loads(packinfo)
    pkgs = pi.get("packages") or []
    pkgname = (pkgs[0].get("name") if pkgs else "entry-release-lite") or "entry-release-lite"

    hap = build_zip(files)                                   # 未签名 hap
    app = build_zip([("pack.info", packinfo),                # ① app 清单
                     (pkgname + ".hap", hap)])               # ② 对应 hap
    open(os.path.join(out_dir, out), "wb").write(app)

    meta.append(dict(out=out, pkg=pkgname, hap=len(hap), app=len(app),
                     bundleName=pi.get("summary", {}).get("app", {}).get("bundleName"),
                     ver=pi.get("summary", {}).get("app", {}).get("version", {}).get("name"),
                     deviceTypes=pi.get("summary", {}).get("modules", [{}])[0].get("deviceType")))
    print("%-18s app=%8d  entries=[pack.info, %s.hap]  bundle=%s v%s dev=%s"
          % (out, len(app), pkgname, meta[-1]["bundleName"], meta[-1]["ver"], meta[-1]["deviceTypes"]))

json.dump(meta, open(os.path.join(out_dir, "meta.json"), "w"), ensure_ascii=False, indent=1)
print("done", len(meta))