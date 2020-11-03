from pathlib import Path
import shutil


def move_files_to_temp_folder(tmp_path, pos=False, poi=False, cons=False):
    org = lambda name: Path(f'./data/{name}.csv')
    tmp = lambda name: tmp_path.joinpath(f'{name}.csv')
    cpy = lambda name: shutil.copy(org(name), tmp(name))
    
    if pos: cpy('posicoes')
    if poi: cpy('base_pois_def')
    if pos: cpy('resultados_consolidado_POIs')