import ftplib
import os

import config


def create_file_if_needed(path_to_file: str) -> None:
    if not os.path.exists(path_to_file):
        open(path_to_file, 'w').close()


def get_ftp_file(path_to_src_file, src_file, path_to_res_file):
    full_path_to_res = os.path.join(path_to_res_file, src_file)
    with ftplib.FTP(config.TIRVIM_FTP_HOST, config.TIRVIM_FTP_USER, config.TIRVIM_FTP_PASS) as ftp:
        ftp.cwd(path_to_src_file)
        create_file_if_needed(full_path_to_res)
        with open(full_path_to_res, 'wb') as f:
            ftp.retrbinary(f'RETR {src_file}', f.write)
    return full_path_to_res
