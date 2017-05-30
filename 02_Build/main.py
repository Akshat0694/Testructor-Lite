from __future__ import print_function
from scrapper import *
import os
import config_file
import easygui
from tqdm import tqdm
from plagiarism import *
import hashlib


def main():
    """Entry point to the script

    This function does the following:
    a. calls the file_download function to download the files from a web location
    b. Checks for plagiarism
    c. generates success report
    """
    import datetime

    try:
        test_takers_list = test_takers()

        # creating required directories
        if not os.path.exists(config_file.rep_dir):
            os.mkdir(config_file.rep_dir)

        if not os.path.exists(config_file.answer_folder):
            os.mkdir(config_file.answer_folder)

        date_time_stamp = str(datetime.datetime.now())

        ans_folder_name = os.path.join(config_file.answer_folder, "Answers_" + date_time_stamp)
        if not os.path.exists(ans_folder_name):
            os.mkdir(ans_folder_name)

        rep_folder_name = os.path.join(config_file.rep_dir, "Report_" + date_time_stamp)
        if not os.path.exists(rep_folder_name):
            os.mkdir(rep_folder_name)

        # downloading answers and working on success report file
        with open(os.path.join(config_file.rep_dir, rep_folder_name, "report " + date_time_stamp + ".csv"),
                  "w") as report_file:
            report_file.write("_" * 75 + "\n")
            report_file.write(
                " Test Taker " + "| Tasks " + "  |                 Status                |" + "  File Name  " + "\n")
            report_file.write("-" * 75 + "\n")

            for test_taker in tqdm(test_takers_list):
                for tasks_folder in config_file.tasks_folders:
                    # fileurl = "http://users.fs.cvut.cz/~" + test_taker + "/" + tasks_folder + "/test.docx"
                    # fileurl = "http://users.fs.cvut.cz/~" + test_taker + "/test.docx"
                    usr_folder = config_file.web_url + test_taker
                    folder_url = config_file.web_url + test_taker + "/" + tasks_folder
                    if file_fldr_exists(usr_folder):
                        folder_name = file_download(folder_url)

                        if folder_name != 0:
                            os.rename(tasks_folder, tasks_folder + ".html")
                            existing_files = filenames_from_html(os.path.join(os.getcwd(), tasks_folder + ".html"))
                            os.remove(os.path.join(os.getcwd(), tasks_folder + ".html"))
                            if len(existing_files) > 0:
                                for file_name in existing_files:
                                    file_url = folder_url + "/" + file_name
                                    file_name = file_download(file_url)

                                    dest_usr = os.path.join(ans_folder_name, test_taker)
                                    if not os.path.exists(dest_usr):
                                        os.mkdir(dest_usr)

                                    dest_task = os.path.join(ans_folder_name, test_taker, tasks_folder)
                                    if not os.path.exists(dest_task):
                                        os.mkdir(dest_task)

                                    move_file(file_name, test_taker, tasks_folder, ans_folder_name)

                                    # Report specific data
                                    success_text_report = "  " + test_taker + "  | " + tasks_folder + " |      Files successfully downloaded      | " + file_name + "\n"
                                    report_file.write(success_text_report)

                            else:
                                # Report specific data
                                no_files_found = "  " + test_taker + "  | " + tasks_folder + " |No files found in the folder to download |" + "\n"
                                report_file.write(no_files_found)

                        else:
                            # Report specific data
                            folder_not_found = "  " + test_taker + "  | " + tasks_folder + " |      Folder named " + tasks_folder + " not found       |" + "\n"
                            report_file.write(folder_not_found)

                    else:
                        # Report specific data
                        error_dwnld_file = "  " + test_taker + "  | " + tasks_folder + " |Can't access url or user folder not found|" + "\n"
                        report_file.write(error_dwnld_file)

                report_file.write(" " + "." * 75 + "\n")
            report_file.write(" " + "-" * 75 + "\n")
            report_file.close()

        if easygui.ynbox("Done downloading files and creating report. \n\nDo you want to run the plagiarism check now?",
                         "Run plagiarism check?", choices=("[<F1>]Yes", "[<F2>]No"),
                         default_choice="[<F1>]Yes", cancel_choice="[<F2>]No"):
            if not config_file.hash_check:
                combs = {}
                final_results = {}
                for Answer_folder in tqdm(retrieve_folder_content(config_file.answer_folder)):
                    for Student_folder in retrieve_folder_content(Answer_folder):
                        for Task_folder in retrieve_folder_content(Student_folder):
                            for Ans_file in retrieve_folder_content(Task_folder, True):
                                # Student_folder2 is the student folder to compare the Ans_file content with
                                for Student_folder2 in retrieve_folder_content(Answer_folder):
                                    if Student_folder2 != Student_folder:
                                        # Task_folder2 is the Task folder inside the Student_folder2 to compare the Ans_file with
                                        for Task_folder2 in retrieve_folder_content(Student_folder2):
                                            if os.path.basename(Task_folder2) == os.path.basename(Task_folder):
                                                stu_fol_1 = os.path.basename(Student_folder)
                                                stu_fol_2 = os.path.basename(Student_folder2)
                                                # stu_tskfile_1 = os.path.basename(Ans_file)
                                                temp_comb = [
                                                    stu_fol_1 + "_" + stu_fol_2 + "_" + os.path.basename(Task_folder),
                                                    stu_fol_2 + "_" + stu_fol_1 + "_" + os.path.basename(Task_folder)]
                                                if temp_comb[0] not in combs:
                                                    for Ans_file2 in retrieve_folder_content(Task_folder2, True):
                                                        with open(Ans_file2, 'r') as fp2:
                                                            with open(Ans_file, 'r') as fp:
                                                                s = fp.read()
                                                                s_tocomp = fp2.read()
                                                                result = fuzz.ratio(s, s_tocomp)
                                                                combs.update(
                                                                    {temp_comb[0]: result, temp_comb[1]: result})
                                                                final_results.update({temp_comb[0]: result})
                print(final_results)

            else:
                combs = {}
                final_results = {}
                for Answer_folder in tqdm(retrieve_folder_content(config_file.answer_folder)):
                    for Student_folder in retrieve_folder_content(Answer_folder):
                        for Task_folder in retrieve_folder_content(Student_folder):
                            for Ans_file in retrieve_folder_content(Task_folder, True):
                                with open(Ans_file, 'r') as fp:
                                    # Student_folder2 is the student folder to compare the Ans_file content with
                                    for Student_folder2 in retrieve_folder_content(Answer_folder):
                                        if Student_folder2 != Student_folder:
                                            # Task_folder2 is the Task folder inside the Student_folder2 to compare the Ans_file with
                                            for Task_folder2 in retrieve_folder_content(Student_folder2):
                                                if os.path.basename(Task_folder2) == os.path.basename(Task_folder):
                                                    stu_fol_1 = os.path.basename(Student_folder)
                                                    stu_fol_2 = os.path.basename(Student_folder2)
                                                    # stu_tskfile_1 = os.path.basename(Ans_file)
                                                    temp_comb = [stu_fol_1 + "_" + stu_fol_2 + "_" + os.path.basename(
                                                        Task_folder),
                                                                 stu_fol_2 + "_" + stu_fol_1 + "_" + os.path.basename(
                                                                     Task_folder)]
                                                    if temp_comb[0] not in combs:
                                                        for Ans_file2 in retrieve_folder_content(Task_folder2, True):
                                                            with open(Ans_file2, 'r') as fp2:
                                                                s_buf = fp.read()

                                                                hasher = hashlib.md5()
                                                                hasher.update(s_buf)
                                                                s = hasher.digest()
                                                                s_tocomp_buf = fp2.read()

                                                                hasher = hashlib.md5()
                                                                hasher.update(s_tocomp_buf)
                                                                s_tocomp = hasher.digest()
                                                                result = fuzz.ratio(s, s_tocomp)

                                                                combs.update(
                                                                    {temp_comb[0]: result, temp_comb[1]: result})
                                                                final_results.update({temp_comb[0]: result})
                print(final_results)

        else:
            pass

        easygui.msgbox("Success!", "Run Result")

    except Exception as err:
        easygui.msgbox("Error!" + "\n" + err.message, "Run Result")
        raise SystemExit(err.message)


if __name__ == "__main__":
    main()
    # pass
