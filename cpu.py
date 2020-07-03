import os
import matplotlib.pyplot as plt  # noqa
import numpy as np
import pandas as pd
import seaborn as sns

parent_dir = '/root/Documents/CPU/statistics/'
cpu_statistics = os.path.join(parent_dir, 'cpu')
memory_statistics = os.path.join(parent_dir, 'memory')
results_dir = os.path.join(parent_dir, 'results')
plots_dir = os.path.join(parent_dir, 'plots')
begin = 0
end = 500


def prepare_memory_df(tool):
    str_file = os.path.join(memory_statistics, tool)
    memory_statistics_files = os.listdir(str_file)
    #os.system('rm {}/{}/*.*'.format(memory_statistics, tool))
    temp_df = pd.DataFrame()

    for index_a, f in enumerate(memory_statistics_files):
        f_name = f.split('.')
        curr_file = os.path.join(str_file, f)

        file = pd.read_fwf(curr_file)

        # prepare dataframe
        #file.drop(file.tail(1).index, inplace=True)  # drop last n rows
        data = file.to_numpy()
        body = data[1:, :]  # filter first rows header
        header = data[:1, :]
        header = header[0]
        new_header = []
        for index, i in enumerate(header):
            if index == 0:
                new_header.append('Time')
            else:
                new_header.append(i)

        # build dataframe
        df = pd.DataFrame(data=body, columns=new_header)

        # replace , x . column
        df['tool'] = tool
        df['iteration'] = index_a
        df['file'] = f_name[0]
        df['%memused'] = [ele.replace(',', '.') for ele in df['%memused']]
        df['%commit'] = [ele.replace(',', '.') for ele in df['%commit']]
        # build df
        temp_df = temp_df.append(df, sort=True, ignore_index=True, verify_integrity=True)

    # data type
    elem = list(temp_df.keys())
    elem.remove('Time')
    elem.remove('tool')
    temp_df[elem] = temp_df[elem].apply(pd.to_numeric)
    temp_df['Time'] = temp_df['Time'].astype('datetime64[ns]').dt.time

    # filter
    memory = temp_df
    memory_data = memory.filter(['%commit', 'iteration', 'tool', 'Time', 'file'], axis=1)
    memory_data.to_csv(os.path.join(results_dir, 'memory', '{}.csv'.format(tool)))


def prepare_cpu_df(tool):
    str_file = os.path.join(cpu_statistics, tool)
    cpu_statistics_files = os.listdir(str_file)
    #os.system('rm {}/{}/*.*'.format(cpu_statistics, tool))
    temp_df = pd.DataFrame()

    for index_a, f in enumerate(cpu_statistics_files):
        f_name = f.split('.')
        curr_file = os.path.join(str_file, f)
        file = pd.read_fwf(curr_file)

        # prepare dataframe
        file.drop(file.tail(1).index, inplace=True)  # drop last n rows
        data = file.to_numpy()
        body = data[1:, :]  # filter first 2 rows ALL CPUs
        header = data[:1, :]
        header = header[0]

        new_header = []
        for index, i in enumerate(header):
            if index == 0:
                new_header.append('Time')
            else:
                new_header.append(i)

        # build dataframe
        df = pd.DataFrame(data=body, columns=new_header)

        # replace , x . column
        df['tool'] = tool
        df['iteration'] = index_a
        df['file'] = f_name[0]
        df['%idle'] = [ele.replace(',', '.') for ele in df['%idle']]
        df['%iowait'] = [ele.replace(',', '.') for ele in df['%iowait']]
        df['%nice'] = [ele.replace(',', '.') for ele in df['%nice']]
        df['%steal'] = [ele.replace(',', '.') for ele in df['%steal']]
        df['%system'] = [ele.replace(',', '.') for ele in df['%system']]
        df['%user'] = [ele.replace(',', '.') for ele in df['%user']]

        temp_df = temp_df.append(df, sort=True, ignore_index=True, verify_integrity=True)

    # data type
    elem = list(temp_df.keys())
    elem.remove('Time')
    elem.remove('tool')
    elem.remove('CPU')
    temp_df[elem] = temp_df[elem].apply(pd.to_numeric)
    temp_df['Time'] = temp_df['Time'].astype('datetime64[ns]').dt.time

    #temp_df[['%idle', '%iowait', '%nice', '%steal', '%system', '%user', 'file']] = temp_df[['%idle', '%iowait', '%nice', '%steal', '%system', '%user', 'file']].apply(pd.to_numeric)

    cpu = temp_df
    cpu_data = cpu.filter(['CPU', '%idle', 'iteration', 'tool', 'Time', 'file'], axis=1)
    filter_string = ['all']
    cpu_data = cpu_data[cpu_data.CPU.isin(filter_string)]
    cpu_data.to_csv(os.path.join(results_dir, 'cpu', '{}.csv'.format(tool)))


def plot_cpu():
    cpu_dir = os.path.join(results_dir, 'cpu')
    result_files = os.listdir(cpu_dir)

    for f in result_files:
        name = f.split('.')
        if name[0] == 'osm':
            df_osm = pd.read_csv(os.path.join(cpu_dir, f))
        elif name[0] == 'omnet':
            df_omnet = pd.read_csv(os.path.join(cpu_dir, f))
        else:
            print('ERROR TOOL NAME !!!!!!!!')

    df_osm = df_osm[df_osm.file >= begin]
    df_omnet = df_omnet[df_omnet.file >= begin]

    df_osm = df_osm[df_osm.file <= end]
    df_omnet = df_omnet[df_omnet.file <= end]

    data = pd.concat([df_osm, df_omnet], ignore_index=True)

    # setup style
    sns.set(font_scale=1.2, rc={'text.usetex': True}, style="whitegrid",
            palette=sns.palplot(sns.color_palette('Paired')), color_codes=True)

    f, axes = plt.subplots(1, 1, figsize=(5, 5), sharex=False, sharey=False)
    sns.despine(left=False, top=False, right=False)

    # Line PLOT
    ###############################
    f1 = sns.lineplot(data=data, x='file', y='%idle', hue='tool')

    # BAR PLOT
    ###############################
    #new_data = data.groupby(['tool'])['%idle'].agg(['mean', 'std']).reset_index()
    #f1 = sns.barplot(data=data, y=r'%idle', x=r'tool')
    ###############################

    # Axes names
    f1.set(ylabel=r'\% IDLE', xlabel=r'Time[s]')
    plt.tight_layout()
    f.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'cpu.pdf'), bbox_inches="tight")


def plot_memory():
    memory_dir = os.path.join(results_dir, 'memory')
    result_files = os.listdir(memory_dir)

    for f in result_files:
        name = f.split('.')
        if name[0] == 'osm':
            df_osm = pd.read_csv(os.path.join(memory_dir, f))
        elif name[0] == 'omnet':
            df_omnet = pd.read_csv(os.path.join(memory_dir, f))
        else:
            print('ERROR TOOL NAME !!!!!!!!')

    df_osm = df_osm[df_osm.file >= begin]
    df_omnet = df_omnet[df_omnet.file >= begin]

    df_osm = df_osm[df_osm.file <= end]
    df_omnet = df_omnet[df_omnet.file <= end]

    data = pd.concat([df_osm, df_omnet], ignore_index=True)

    # setup style
    #sns.set(font_scale=1.2, rc={'text.usetex': True}, style="whitegrid",
    #        palette=sns.palplot(sns.color_palette('Paired')), color_codes=True)

    f, axes = plt.subplots(1, 1, figsize=(5, 5), sharex=False, sharey=False)
    sns.despine(left=False, top=False, right=False)

    # Line PLOT
    ###############################
    f1 = sns.lineplot(data=data, x='file', y=r'%commit', hue='tool')

    # BAR PLOT
    ###############################
    #new_data = data.groupby(['tool'])['%idle'].agg(['mean', 'std']).reset_index()
    #f1 = sns.barplot(data=data, x=r'tool', y=r'%commit')
    ###############################

    # Axes names
    f1.set(ylabel=r'\% MEMORY', xlabel=r'Time[s]')
    plt.tight_layout()
    f.tight_layout()
    plt.savefig(os.path.join(plots_dir, 'memory.pdf'), bbox_inches="tight")


if __name__ == '__main__':
    tools = ['osm', 'omnet']

    for t in tools:
        prepare_cpu_df(t)
        prepare_memory_df(t)

    plot_cpu()
    plot_memory()