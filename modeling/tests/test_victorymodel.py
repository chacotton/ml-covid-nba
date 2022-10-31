from modeling.chance_of_victory import NBACoV
import pandas as pd
import numpy as np
import paramiko
import zipfile
import os
import shutil
import pytest


@pytest.fixture(scope="module", autouse=True)
def files():
    file = 'classifier_v2'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname='129.153.2.48', username='team', password='NBACovid19!')
    with ssh.open_sftp() as sftp:
        sftp.get(f'/mnt/ml-nba/models/{file}.zip', f'./{file}.zip')
    ssh.close()
    with zipfile.ZipFile(f'{file}.zip', 'r') as f:
        f.extractall('./')
    yield
    os.remove('classifier_v2.zip')
    shutil.rmtree('classifier_v2')


class TestChanceOfVictory:
    def test_init_cov(self):
        cov = NBACoV('classifier_v2')
        assert cov

    def test_predict(self):
        assert True
