import glob
import random
import subprocess
from datetime import datetime

import nfc

import create_table
import reader
import slack_post


def connected(tag):

    if isinstance(tag, nfc.tag.tt3.Type3Tag):
        try:
            if tag.sys == 0x8688:
                # 京都大学学生証
                student_id, student_name = reader.read_kucard(tag)
                time = datetime.now()
                exists, visited = create_table.table_management(
                    student_id, student_name, time
                )
                if not exists:
                    slack_post.enter(time, student_name)
                    if not visited:
                        subprocess.run(["aplay", "./default_sounds/famima.wav"])
                    else:
                        sound = random.choice(glob.glob("./enter_sounds/*"))
                        if sound.rsplit(".", 1)[1].lower() == "wav":
                            subprocess.run(["aplay", sound])
                        else:  # mp3
                            subprocess.run(["mpg321", sound])
                else:
                    slack_post.leave(time, student_name)
                    sound = random.choice(glob.glob("./exit_sounds/*"))
                    if sound.rsplit(".", 1)[1].lower() == "wav":
                        subprocess.run(["aplay", sound])
                    else:  # mp3
                        subprocess.run(["mpg321", sound])
            elif tag.sys == 0x0003:
                # 交通系icカード
                balance = reader.read_suica(tag)
                slack_post.balance_check(balance)
                subprocess.run(["aplay", "default_sounds/suica_beep.wav"])
        except KeyboardInterrupt:
            print("interrupt")
            exit()
        except Exception as e:
            slack_post.miss()
            print("Error:%s" % e)
    else:
        print("Error:tag isn't Type3Tag")

    return True


def main():
    while True:
        with nfc.ContactlessFrontend("usb") as clf:
            clf.connect(rdwr={"on-connect": connected})


if __name__ == "__main__":
    main()
