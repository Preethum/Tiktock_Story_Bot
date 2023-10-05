import subprocess
import Reddit


reddit_link = []
reddit_data = Reddit.set_up_config_settings()
main_link = "RedditClips\main.py"

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
            powershell_command = f"python3 {main_link} -l {link}"
            # subprocess.run(['powershell.exe', '-Command', "clear"], check=True)
            process = subprocess.run(
                ["powershell.exe", "-Command", powershell_command], check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Process failed with return code {e.returncode}.")
        except Exception as e:
            print("An error occurred:", str(e))


def custom_tns(title, story):
    try:
        powershell_command = f'python3 {main_link} -t "{title}" -s "{story}"'
        # subprocess.run(['powershell.exe', '-Command', "clear"], check=True)
        process = subprocess.run(
            ["powershell.exe", "-Command", powershell_command], check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Process failed with return code {e.returncode}.")
    except Exception as e:
        print("An error occurred:", str(e))


def run_txt_tns():
    file_path = "RedditClips\\tns_data.txt"
    delimiter = "~"
    with open(file_path, "r") as file:
        lines = file.readlines()
    split_lines = [line.strip().split(delimiter) for line in lines]
    for link in split_lines:
        # print(link)

        try:
            powershell_command = f'python3 {main_link} -t "{link[0]}" -s "{link[1]}"'
            # subprocess.run(['powershell.exe', '-Command', "clear"], check=True)
            process = subprocess.run(
                ["powershell.exe", "-Command", powershell_command], check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Process failed with return code {e.returncode}.")
        except Exception as e:
            print("An error occurred:", str(e))


print(
    """
1. Generate only one link
2. Generate top X ammount
3. Pull From List
4. Custom Title and Story
5. Custom Title and Story From File
"""
)
user_input_list = []
user_input = int(input("Selection: "))
if user_input == 1:
    link = input("Enter link here: ")
    reddit_link.append(link)
    run_main(reddit_link)
elif user_input == 2:
    number_top_posts = input("Enter number of top posts: ")
    reddit_link = Reddit.find_top_posts(reddit_data, "stories", int(number_top_posts))
    run_main(reddit_link)
elif user_input == 3:
    keyword = "stop"
    while True:
        user_input = input("Enter a reddit link (type 'stop' to end input): ")
        if user_input.lower() == keyword:
            break  # Exit the loop if the keyword is entered
        user_input_list.append(user_input)
    run_main(user_input_list)
elif user_input == 4:
    title = input("Enter Title: ")
    story = input("Enter Story: ")
    custom_tns(title, story)
elif user_input == 5:
    print("Reading tns_data.txt")
    run_txt_tns()

else:
    print("Invalid arg")
