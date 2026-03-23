import read_ad
import re

def return_ad_mail(system_login):
    try:
        return read_ad.get_first_user(system_login).mail
    except:
        return False

def return_ad_status(system_login):
    try:
        return read_ad.get_first_user(system_login).URRoleStatus
    except:
        return False

def search_active(ur_status):
    return bool(re.search(r"HRMS.+Active", ur_status))

def confirm_active(system_login):
    if (captured_status := return_ad_status(system_login)):
        if type(captured_status) is tuple:
            return any(map(search_active, captured_status))
        else:
            return bool(re.search(r"HRMS.+Active", captured_status))

def return_full_name(system_login):
    try:
        return read_ad.get_first_user(system_login).cn
    except:
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ad_functions.py <system_login>")
        sys.exit(1)

    system_login = sys.argv[1]
    print(read_ad.get_first_user(system_login))
    print(return_ad_mail(system_login))
    print(return_full_name(system_login))
    print(return_ad_status(system_login))
    print(confirm_active(system_login))