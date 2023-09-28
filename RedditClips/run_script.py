import subprocess
import Reddit

reddit_link = []
reddit_data = Reddit.set_up_config_settings()
powershell_command = "main.py"

print(
    """

 _______                   __        __  __    __             ______    __                                             
/       \                 /  |      /  |/  |  /  |           /      \  /  |                                            
$$$$$$$  |  ______    ____$$ |  ____$$ |$$/  _$$ |_         /$$$$$$  |_$$ |_     ______    ______   __    __   _______ 
$$ |__$$ | /      \  /    $$ | /    $$ |/  |/ $$   |        $$ \__$$// $$   |   /      \  /      \ /  |  /  | /       |
$$    $$< /$$$$$$  |/$$$$$$$ |/$$$$$$$ |$$ |$$$$$$/         $$      \$$$$$$/   /$$$$$$  |/$$$$$$  |$$ |  $$ |/$$$$$$$/ 
$$$$$$$  |$$    $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ | __        $$$$$$  | $$ | __ $$ |  $$ |$$ |  $$/ $$ |  $$ |$$      \ 
$$ |  $$ |$$$$$$$$/ $$ \__$$ |$$ \__$$ |$$ |  $$ |/  |      /  \__$$ | $$ |/  |$$ \__$$ |$$ |      $$ \__$$ | $$$$$$  |
$$ |  $$ |$$       |$$    $$ |$$    $$ |$$ |  $$  $$/       $$    $$/  $$  $$/ $$    $$/ $$ |      $$    $$ |/     $$/ 
$$/   $$/  $$$$$$$/  $$$$$$$/  $$$$$$$/ $$/    $$$$/         $$$$$$/    $$$$/   $$$$$$/  $$/        $$$$$$$ |$$$$$$$/  
                                                                                                   /  \__$$ |          
                                                                                                   $$    $$/           
                                                                                                    $$$$$$/"""
)


def run_main(reddit_link):
    for link in reddit_link:
    
        try:
            command = f'start powershell.exe -NoExit -Command python3 "{powershell_command} -l {link}"'    
            process = subprocess.Popen(command, shell=True)
            process.wait()
        except Exception as e:
            print("An error occurred:", str(e))


print(
    """
1. Generate only one link
2. Generate top X ammount
"""
)
user_input = int(input("Selection: "))
if user_input == 1:
    link = input("Enter link here: ")
    reddit_link.append(link)
    run_main(reddit_link)
elif user_input == 2:
    number_top_posts = input("Enter number of top posts: ")
    reddit_link = Reddit.find_top_posts(reddit_data, "stories", int(number_top_posts))
    run_main(reddit_link)
else:
    print("Invalid arg")
