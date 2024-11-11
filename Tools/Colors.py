# Regular Colors
black = "\033[0;30m"
red = "\033[0;31m"
green = "\033[0;32m"
yellow = "\033[0;33m"
blue = "\033[0;34m"
magenta = "\033[0;35m"
cyan = "\033[0;36m"
white = "\033[0;37m"

# Bold Colors (Bright)
bold_black = "\033[1;30m"
bold_red = "\033[1;31m"
bold_green = "\033[1;32m"
bold_yellow = "\033[1;33m"
bold_blue = "\033[1;34m"
bold_magenta = "\033[1;35m"
bold_cyan = "\033[1;36m"
bold_white = "\033[1;37m"

# Underline Colors
underline_black = "\033[4;30m"
underline_red = "\033[4;31m"
underline_green = "\033[4;32m"
underline_yellow = "\033[4;33m"
underline_blue = "\033[4;34m"
underline_magenta = "\033[4;35m"
underline_cyan = "\033[4;36m"
underline_white = "\033[4;37m"

# Background Colors
background_black = "\033[40m"
background_red = "\033[41m"
background_green = "\033[42m"
background_yellow = "\033[43m"
background_blue = "\033[44m"
background_magenta = "\033[45m"
background_cyan = "\033[46m"
background_white = "\033[47m"

# Bright Background Colors
background_bright_black = "\033[100m"
background_bright_red = "\033[101m"
background_bright_green = "\033[102m"
background_bright_yellow = "\033[103m"
background_bright_blue = "\033[104m"
background_bright_magenta = "\033[105m"
background_bright_cyan = "\033[106m"
background_bright_white = "\033[107m"

# Bold Colors
bold_bright_red = "\033[1;91m"
bold_bright_green = "\033[1;92m"
bold_bright_yellow = "\033[1;93m"
bold_bright_blue = "\033[1;94m"
bold_bright_magenta = "\033[1;95m"
bold_bright_cyan = "\033[1;96m"

# Reset
reset = "\033[0m"

if __name__=="__main__":
    # Regular Colors
    print(f"{black}This is testing Regular Color text{reset}")
    print(f"{red}This is testing Regular Color text{reset}")
    print(f"{green}This is testing Regular Color text{reset}")
    print(f"{yellow}This is testing Regular Color text{reset}")
    print(f"{blue}This is testing Regular Color text{reset}")
    print(f"{magenta}This is testing Regular Color text{reset}")
    print(f"{cyan}This is testing Regular Color text{reset}")
    print(f"{white}This is testing Regular Color text{reset}\n")

    # Bold Colors (Bright)
    print(f"{bold_black}This is testing Bold Color (Bright) text{reset}")
    print(f"{bold_red}This is testing Bold Color (Bright) text{reset}")
    print(f"{bold_green}This is testing Bold Color (Bright) text{reset}")
    print(f"{bold_yellow}This is testing Bold Color (Bright) text{reset}")
    print(f"{bold_blue}This is testing Bold Color (Bright) text{reset}")
    print(f"{bold_magenta}This is testing Bold Color (Bright) text{reset}")
    print(f"{bold_cyan}This is testing Bold Color (Bright) text{reset}")
    print(f"{bold_white}This is testing Bold Color (Bright) text{reset}\n")

    # Underline Colors
    print(f"{underline_black}This is testing Underline Color text{reset}")
    print(f"{underline_red}This is testing Underline Color text{reset}")
    print(f"{underline_green}This is testing Underline Color text{reset}")
    print(f"{underline_yellow}This is testing Underline Color text{reset}")
    print(f"{underline_blue}This is testing Underline Color text{reset}")
    print(f"{underline_magenta}This is testing Underline Color text{reset}")
    print(f"{underline_cyan}This is testing Underline Color text{reset}")
    print(f"{underline_white}This is testing Underline Color text{reset}\n")

    # Background Colors
    print(f"{background_black}This is testing Background Color text{reset}")
    print(f"{background_red}This is testing Background Color text{reset}")
    print(f"{background_green}This is testing Background Color text{reset}")
    print(f"{background_yellow}This is testing Background Color text{reset}")
    print(f"{background_blue}This is testing Background Color text{reset}")
    print(f"{background_magenta}This is testing Background Color text{reset}")
    print(f"{background_cyan}This is testing Background Color text{reset}")
    print(f"{background_white}This is testing Background Color text{reset}\n")

    # Bright Background Colors
    print(f"{background_bright_black}This is testing Bright Background Color text{reset}")
    print(f"{background_bright_red}This is testing Bright Background Color text{reset}")
    print(f"{background_bright_green}This is testing Bright Background Color text{reset}")
    print(f"{background_bright_yellow}This is testing Bright Background Color text{reset}")
    print(f"{background_bright_blue}This is testing Bright Background Color text{reset}")
    print(f"{background_bright_magenta}This is testing Bright Background Color text{reset}")
    print(f"{background_bright_cyan}This is testing Bright Background Color text{reset}")
    print(f"{background_bright_white}This is testing Bright Background Color text{reset}\n")

    # Bold Colors
    print(f"{bold_bright_red}This is testing Bold Color text{reset}")
    print(f"{bold_bright_green}This is testing Bold Color text{reset}")
    print(f"{bold_bright_yellow}This is testing Bold Color text{reset}")
    print(f"{bold_bright_blue}This is testing Bold Color text{reset}")
    print(f"{bold_bright_magenta}This is testing Bold Color text{reset}")
    print(f"{bold_bright_cyan}This is testing Bold Color text{reset}")