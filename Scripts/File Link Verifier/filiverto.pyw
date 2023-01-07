# filiverto is the File Link Verifier for AbstractSpoon's ToDoList.

import csv
import os
import re
import sys
import tkinter as tk
import urllib.parse
from tkinter import filedialog, messagebox

# lxml is not part of the standard library.
# Install it from the command line with "pip install lxml.
from lxml import etree


def check_and_add(id, full_link, missing_files):
    """
    Verifies that a file exists; if it is missing, adds it to the list of missing
    files.
    full_link contains the match as it was found and how it will appear
    in the report.
    clean_link is the content of full_link formatted so that it can be used to
    verify the existence of the file or directory.
    """
    if "tdl://" in full_link:

        # Remove the protocol identifier and direct task id references
        # for other task lists, such as tdl://test.tdl?1234.
        # Remove potentially trailing period characters from the punctuation
        # in the surrounding text; a legal file name must not end with a period.
        clean_link = re.sub(r"tdl:/{2,3}", "", full_link)
        clean_link = clean_link.split("?", 1)[0].rstrip(".")

        if len(clean_link.strip()) == 0 or clean_link.isnumeric():
            # Empty link or link to a task in the same ToDoList; nothing to do.
            return
    elif "file://" in full_link:
        clean_link = re.sub(r"file:/{2,3}", "", full_link)
        clean_link = clean_link.rstrip(".")
        if len(clean_link.strip()) == 0:
            # Empty link; nothing to do.
            return
    elif "//" in full_link:
        # All other protocols/hyperlinks are ignored.
        return
    else:
        # If there is no preceding protocol identifiier,
        # the full link and the clean link are the same.
        clean_link = full_link

    # Clean up %20 characters as in tdl://todolist%20test.tdl.
    clean_link = urllib.parse.unquote(clean_link)

    if os.path.isfile(clean_link) == False and os.path.isdir(clean_link) == False:
        missing_files.append({"id": id, "file": full_link})
    return


def process_FILEREFPATH(xml_tree) -> tuple[list, int]:
    """Gather and check links from the FILEREFPATH element."""
    missing_files = []
    filerefpaths = xml_tree.xpath("//FILEREFPATH")
    for filerefpath in filerefpaths:
        id = filerefpath.getparent().attrib["ID"]
        full_link = filerefpath.text
        check_and_add(id, full_link, missing_files)
    return missing_files, len(filerefpaths)


def process_COMMENTS(xml_tree) -> tuple[list, int]:
    """Gather and check links from the COMMENTS element."""
    missing_files = []
    checked_links = 0
    comments_elements = xml_tree.xpath("//COMMENTS")

    for comment_element in comments_elements:
        id = comment_element.getparent().attrib["ID"]
        comments = comment_element.text

        # Match tdl:// that includes spaces, marked by a "<" character.
        re_tdl_spaces = r"(?<=<)tdl://(?:[A-z]:)?[^<>\*\"|?:]*(?=>)"
        # Match tdl:// in parentheses; In that case, the trailing parenthesis
        # has to be excluded from the file path.
        re_tdl_parentheses = r"(?<=\()tdl://(?:[A-z]:)?[^\s<>\*\"|?:]*(?=\))"
        # Match tdl:// without spaces, not embedded in brackes or parentheses.
        re_tdl_no_spaces = r"(?<!\()(?<!<)tdl://(?:[A-z]:)?[^\s<>\*\"|?:]*"
        # Match file:// that includes spaces, embedded in "<>" characters.
        re_file_spaces = r"(?<=<)file:/{2,3}(?:[A-z]:)?[^<>\*\"|?:]*(?=>)"
        # Match file:// in parentheses; In that case, the trailing parenthesis
        # has to be excluded from the file path; there must not be any spaces.
        re_file_no_spaces = (
            r"(?<!\()(?<!<)file:/{2,3}(?:[A-z]:)?[^\s<>\*\"|?:]*|"
            + r"(?<=\()file:/{2,3}(?:[A-z]:)?[^\s<>\*\"|?:]*(?=\))"
        )

        matches = []
        for pattern in [
            re_tdl_spaces,
            re_tdl_parentheses,
            re_tdl_no_spaces,
            re_file_spaces,
            re_file_no_spaces,
        ]:
            matches += re.findall(pattern, comments)
        for match in matches:
            check_and_add(id, match, missing_files)
        checked_links += len(matches)
    return missing_files, checked_links


def save_csv_report(report_path, missing_files) -> int:
    """Save the missing files report as "<<ToDoList name>>_missing_files.csv"."""

    # Make sure that the file is writable
    if os.path.exists(report_path):
        try:
            os.rename(report_path, report_path)
        except OSError as e:
            return 1

    # newline='' is necessary to prevent Excel from showing empty lines.
    # utf-8-sig needs to be chosen as encoding because Excel expects a BOM,
    # otherwise umlauts are not properly displayed.
    with open(report_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        csvwriter = csv.writer(
            csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )

        # CSV header row
        csvwriter.writerow(["Task ID", "File Link"])

        for entry in missing_files:
            csvwriter.writerow([entry["id"], entry["file"]])
    return 0


def main() -> int:
    """
    Prepare the task list, extract and verify, then report the result.

    Check if files that are referenced by task list file links actually exist.
    If not, write the Task IDs and defective file links to a CSV file.
    Only tdl:// and file:// links are checked; so no validation of links to the
    Internet is performed.
    """
    args = sys.argv[1:]
    tk_root = tk.Tk()
    tk_root.withdraw()

    # Try to load the ToDoList icon for the dialogs.
    # It is assumed to be in the same directory as the script.
    icon_path = ""
    icon_path = os.path.dirname(__file__) + "\ToDoList_2004.ico"
    if os.path.isfile(icon_path):
        tk_root.iconbitmap(icon_path)

    # Get the file name for the task list from an argument or
    # by means of a file open dialog.
    if len(args) > 1:
        messagebox.showinfo(
            title="Too many arguments",
            message="Please provide \n* no argument or \n* "
            + "the file name of the ToDoList as the only argument.",
        )
        return 1
    elif len(args) == 1:
        tdl_path = args[0]
    else:
        tdl_path = filedialog.askopenfilename(
            initialdir=".",
            title="For verifiying file links, choose a task list",
            filetypes=[("Abstractspoon ToDoList", ".tdl")],
        )

    if os.path.isfile(tdl_path) == False:
        if len(args) == 1:
            messagebox.showinfo(
                title="File not found",
                message="The file \n" + tdl_path + "\ncould not be found.",
            )
        return 2

    # Set working directory to make sure that relative file links
    # will be evaluated correctly.
    if os.path.dirname(tdl_path):
        os.chdir(os.path.dirname(tdl_path))

    xml_parser = etree.XMLParser(remove_blank_text=True)
    xml_tree = etree.parse(tdl_path, xml_parser)

    # Gather all dangling file references and their task IDs.
    missing_files = []
    num_links = 0
    missing_filerefpath_files, num_filerefpath_links = process_FILEREFPATH(xml_tree)
    missing_comments_files, num_comments_links = process_COMMENTS(xml_tree)
    missing_files = missing_filerefpath_files + missing_comments_files
    num_links = num_filerefpath_links + num_comments_links

    if not missing_files:
        messagebox.showinfo(
            title="Process completed",
            message=str(num_links)
            + f" link{'s'[:num_links^1]} checked.\n"
            + "Congratulations! There are no dangling file references.",
        )
        return 0

    # Save the report file and deal with potential errors
    report_path = tdl_path.rstrip(".tdl") + "_missing_files.csv"
    if save_csv_report(report_path, missing_files) == 0:
        # It's all good
        message_icon = "info"
        msg_text = ""
    else:
        # An error occurred
        if len(os.path.dirname(report_path)) > 30:
            report_path = "...\\" + os.path.basename(report_path)
            message_icon = "error"
        msg_text = (
            f"The report file {report_path} cannot be written. "
            + "It already exists and is in use by another application.\n\n"
        )

    msg_text += f"{str(num_links)} links checked.\n"
    if len(missing_files) > 1:
        msg_text += f"{str(len(missing_files))} defective file links were found."
    else:
        msg_text = "1 defective file link was found."

    messagebox.showinfo(
        title="Process completed",
        message=msg_text,
        icon=message_icon,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
