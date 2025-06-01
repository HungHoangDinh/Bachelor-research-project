import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from constants.constants import MODES, FILE_NAMES,RAGAS_METRICS
def visualize_lines_char(modes:list[str], datas:list[list[int]],metrics:str, image_name:str):
    """
    Visualizes the lines for each mode with the given data.

    Args:
        modes (list[str]): List of modes to visualize.
        datas (list[list[int]]): List of data corresponding to each mode.
    """
    if "(mode=f1)" in metrics:
        metrics = metrics.replace("(mode=f1)", "")
        image_name = image_name.replace("(mode=f1)", "")
    x= list(range(len(datas[0])-4))
    plt.figure(figsize=(12, 6))
    for i, array in enumerate(datas):
        array=array[:len(x)]
        avg = np.mean(array)
        plt.plot(x, array, label=f"{modes[i]}: {avg:.2f}")
    plt.title(metrics)
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'results/images/{image_name}.png', dpi=300)
def visualize_columns_char(total_datas: list, correct_datas: list, modes: list[str]):
    """
    Visualizes the columns for each mode with the given data.

    Args:
        total_datas (list): List of total data values.
        correct_datas (list): List of correct data values.
        modes (list[str]): List of modes to visualize.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import textwrap

    num_bars = len(total_datas)
    spacing = 1.5
    x = np.arange(num_bars) * spacing
    bar_width = 0.35

    # Tự động xuống dòng cho tên mode dài
    wrapped_modes = [textwrap.fill(mode, width=10) for mode in modes]

    plt.figure(figsize=(12, 6))

    for i in range(num_bars):
        ratio = correct_datas[i] / total_datas[i] * 100 if total_datas[i] != 0 else 100
        plt.bar(x[i], total_datas[i], width=bar_width, color='lightgray', zorder=1)
        plt.bar(x[i], correct_datas[i], width=bar_width, color='orange', zorder=2)
        plt.text(x[i], total_datas[i] + 1, f'{ratio:.1f}%', ha='center', fontsize=9)

    plt.xticks(x, wrapped_modes)
    plt.title('Total Information and Correct Information')
    plt.xlabel('Modes')
    plt.ylabel('Count')
    plt.legend(['Total', 'Correct'])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('results/images/total_correct_info.png', dpi=300)

def visualize_RCMMS_03_07():
    """
    Visualizes the columns for each mode with the given data.

    Args:
        total_datas (list): List of total data values.
        correct_datas (list): List of correct data values.
        modes (list[str]): List of modes to visualize.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import textwrap
    data=[0.61,0.68,0.91,0.81,0.61,0.55,0.83,0.77,0.32,0.38]
    num_bars = len(data)
    modes=["RAG","RAG Custom","Local Search","Local Search Custom","Global Search","Global Search Custom","DRIFT Search","DRIFT Search Custom","Google AI Studio","ChatGPT"]
    spacing = 1.5
    x = np.arange(num_bars) * spacing
    bar_width = 0.35

    # Tự động xuống dòng cho tên mode dài
    wrapped_modes = [textwrap.fill(mode, width=10) for mode in modes]

    plt.figure(figsize=(12, 6))

    for i in range(num_bars):
        plt.bar(x[i], data[i], width=bar_width, color='orange', zorder=1)
        plt.text(x[i], data[i] + 0.02, data[i], ha='center', fontsize=9)

    plt.xticks(x, wrapped_modes)
    plt.title('RCMMS when α = 0.3 and β = 0.7')
    plt.xlabel('Modes')
    plt.ylabel('Value')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('results/images/RCMMS_03_07.jpg', dpi=300)
def visualize_RCMMS_05_05():
    """
    Visualizes the columns for each mode with the given data.

    Args:
        total_datas (list): List of total data values.
        correct_datas (list): List of correct data values.
        modes (list[str]): List of modes to visualize.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import textwrap
    data=[0.67,0.73,0.85,0.82,0.64,0.61,0.77,0.78,0.40,0.48]
    num_bars = len(data)
    modes=["RAG","RAG Custom","Local Search","Local Search Custom","Global Search","Global Search Custom","DRIFT Search","DRIFT Search Custom","Google AI Studio","ChatGPT"]
    spacing = 1.5
    x = np.arange(num_bars) * spacing
    bar_width = 0.35

    # Tự động xuống dòng cho tên mode dài
    wrapped_modes = [textwrap.fill(mode, width=10) for mode in modes]

    plt.figure(figsize=(12, 6))

    for i in range(num_bars):
        plt.bar(x[i], data[i], width=bar_width, color='orange', zorder=1)
        plt.text(x[i], data[i] + 0.02, data[i], ha='center', fontsize=9)

    plt.xticks(x, wrapped_modes)
    plt.title('RCMMS when α = 0.5 and β = 0.5')
    plt.xlabel('Modes')
    plt.ylabel('Value')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('results/images/RCMMS_05_05.jpg', dpi=300)
def visualize_RCMMS_07_03():
    """
    Visualizes the columns for each mode with the given data.

    Args:
        total_datas (list): List of total data values.
        correct_datas (list): List of correct data values.
        modes (list[str]): List of modes to visualize.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import textwrap
    data=[0.74,0.78,0.79,0.83,0.66,0.67,0.72,0.79,0.49,0.58]
    num_bars = len(data)
    modes=["RAG","RAG Custom","Local Search","Local Search Custom","Global Search","Global Search Custom","DRIFT Search","DRIFT Search Custom","Google AI Studio","ChatGPT"]
    spacing = 1.5
    x = np.arange(num_bars) * spacing
    bar_width = 0.35

    # Tự động xuống dòng cho tên mode dài
    wrapped_modes = [textwrap.fill(mode, width=10) for mode in modes]

    plt.figure(figsize=(12, 6))

    for i in range(num_bars):
        plt.bar(x[i], data[i], width=bar_width, color='orange', zorder=1)
        plt.text(x[i], data[i] + 0.02, data[i], ha='center', fontsize=9)

    plt.xticks(x, wrapped_modes)
    plt.title('RCMMS when α = 0.7 and β = 0.3')
    plt.xlabel('Modes')
    plt.ylabel('Value')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('results/images/RCMMS_07_03.jpg', dpi=300)
def get_data_ragas(metrics:str):
    """
    Retrieves the data for each mode based on the given metrics.

    Args:
        metrics (str): The metric to retrieve data for.

    Returns:
        list[list[int]]: List of data arrays for each mode.
    """
    datas = []
    
    for index, mode in enumerate(MODES):
        file_name = f"results/eval_{FILE_NAMES[index]}_ragas_result.xlsx"
        df=pd.read_excel(file_name)
        data=df[metrics].tolist()
        datas.append(data)
    return datas
def visualize_ragas():
    """
    Visualizes the RAGAS metrics for each mode and saves the images.
    """
    for metrics in RAGAS_METRICS:
        datas = get_data_ragas(metrics)
        for i in range(4):
            files= FILE_NAMES[i*2:i*2+2]
            modes= MODES[i*2:i*2+2]
            datas_subset = [datas[j] for j in range(i*2, i*2+2)]
            visualize_lines_char(modes, datas_subset, metrics, f"{metrics}_{files[0]}_{files[1]}")
    print("Visualization completed and saved in results/images/")
def visualize_no_rag():
    
    file_name= "results/data_total_info.xlsx"
    df = pd.read_excel(file_name)
    total=[]
    for mode in MODES:
        total.append(df[mode].sum())
    file_name = "results/data_correct_info.xlsx"
    df = pd.read_excel(file_name)
    correct=[]
    for mode in MODES:
        correct.append(df[mode].sum())
    visualize_columns_char(total, correct, MODES)
if __name__ == "__main__":
    # visualize_ragas()
    # visualize_no_rag()
    # visualize_RCMMS_03_07()
    visualize_RCMMS_05_05()
    visualize_RCMMS_07_03()
    print("Visualization completed and saved in results/images/")