from datetime import datetime,timezone

def error_log(message,error):
    try:
        utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        with open ("error_log.txt", "a", encoding="utf8") as log_file:
            log_file.write(utc_time + ", " + str(message).replace("\r", r"\r").replace("\n", r"\n") + ", " + str(error).replace("\r", r"\r").replace("\n", r"\n") + "\n")
        print(message)
        print(error)
    except Exception as e:
        print("Could not write to error log:")
        print(e)
