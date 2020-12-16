import nfc
import struct

def read_kucard(tag):
    servc = 0x1A8B
    service_code = [nfc.tag.tt3.ServiceCode(servc >> 6, servc & 0x3F)]

    tag.dump()

    bc_id = [nfc.tag.tt3.BlockCode(0)]
    bd_id = tag.read_without_encryption(service_code, bc_id)
    student_id = int(bd_id[2:-4].decode("utf-8"))

    bc_name = [nfc.tag.tt3.BlockCode(1)]
    student_name = (
        tag.read_without_encryption(service_code, bc_name)
        .decode("shift-jis")
        .rstrip("\x00")
    )

    return student_id, student_name


def read_suica(tag):
    servc = 0x090F
    service_code = [nfc.tag.tt3.ServiceCode(servc >> 6, servc & 0x3F)]
    block_code = [nfc.tag.tt3.BlockCode(0, service=0)]
    row_le = struct.unpack(
        "<2B2H4BH4B", tag.read_without_encryption(service_code, block_code)
    )
    balance = row_le[8]

    return balance
