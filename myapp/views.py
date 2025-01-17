
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect,FileResponse
from django.urls import reverse
from .forms import UploadFileForm, SelectColumnForm,GraphTypeForm
from windrose import WindroseAxes
from matplotlib.cm import viridis
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import calendar
import os
from django.conf import settings 
import matplotlib
matplotlib.use('Agg')  
plt.ioff()

def process_file(file_path):
    dataframe = pd.read_csv(file_path)
    columns = dataframe.columns.tolist()
    return dataframe, columns

def select_graph_type(request):
    if request.method == 'POST':
        form = GraphTypeForm(request.POST)
        if form.is_valid():
            graph_type = form.cleaned_data['graph_type']
            request.session['graph_type'] = graph_type
            if graph_type == 'monthly_yearly_mean':
                return redirect('select_columns')  # Redirect to select Y-axis for the first plot
            else:
                return redirect('generate_graph')
    else:
        form = GraphTypeForm()
    return render(request, 'select_graph_type.html', {'form': form})

def generate_graph(request):
    graph_type = request.session.get('graph_type')
    file_path = request.session.get('file_path')

    if not file_path:
        return redirect('upload_file') 
    
    dataframe = pd.read_csv(file_path)
    dataframe['DATETIME'] = pd.to_datetime(dataframe['DATE'] + ' ' + dataframe['TIME(UTC)'])

    plot_paths=[]

    if graph_type == 'Yearly_mean_for_temp':
        plot_paths.append (generate_yearly_mean_for_temp(dataframe))

    elif graph_type == 'Yearly_mean_for_max_daily_temp':
        plot_paths.append(generate_yearly_mean_for_max_daily_temp(dataframe))

    elif graph_type == 'daily_max_temp':
        plot_paths.extend(generate_daily_max_temp(dataframe))

    elif graph_type == 'wind_rose':
        plot_paths.extend(generate_wind_rose(dataframe))

    if plot_paths:  # Ensure plot_path is valid before storing
        request.session['plot_paths'] = plot_paths
    else:
        request.session['plot_paths'] = None 

    return redirect('results')

def generate_plots_and_csv(dataframe, y_col):
    dataframe['DATETIME'] = pd.to_datetime(dataframe['DATE'] + ' ' + dataframe['TIME(UTC)'])
    dataframe['Month'] = dataframe['DATETIME'].dt.month
    dataframe['Hour'] = dataframe['DATETIME'].dt.hour

    def calculate_hourly_means_and_stds(dataframe, month):
        monthly_data = dataframe[dataframe['Month'] == month]
        hourly_means = monthly_data.groupby('Hour')[y_col].apply(np.nanmean)
        hourly_stds = monthly_data.groupby('Hour')[y_col].apply(np.nanstd)
        return hourly_means, hourly_stds

    months = range(1, 13)
    month_names = [calendar.month_name[month] for month in months]

    global_min = float('inf')
    global_max = float('-inf')

    all_months_data = {}

    for month in months:
        hourly_means, hourly_stds = calculate_hourly_means_and_stds(dataframe, month)
        if not hourly_means.empty:
            global_min = min(global_min, hourly_means.min() - hourly_stds.max())
            global_max = max(global_max, hourly_means.max() + hourly_stds.max())

    plt.figure(figsize=(15, 20))

    for i, (month, month_name) in enumerate(zip(months, month_names), 1):
        hourly_means, hourly_stds = calculate_hourly_means_and_stds(dataframe, month)
        if not hourly_means.empty:
            plt.subplot(6, 2, i)
            plt.errorbar(hourly_means.index, hourly_means.values, yerr=hourly_stds.values, color='red', marker='o', capsize=2)
            plt.title(f'Mean {y_col} for {month_name}')
            plt.xlabel('Hour of Day')
            plt.ylabel(f'Mean {y_col}')
            plt.xticks(range(0, 24, 2))
            plt.ylim(global_min, global_max)

            csv_data = {
                'Hour': [month_name] + list(hourly_means.index),
                f'Mean {y_col}': [''] + list(hourly_means.values),
                f'Standard Deviation ({y_col})': [''] + list(hourly_stds.values)
            }

            month_data_df = pd.DataFrame(csv_data)
            all_months_data[month_name] = month_data_df

    combined_data = pd.DataFrame()
    for month_name in month_names:
        if month_name in all_months_data:
            combined_data = pd.concat(
                [combined_data, all_months_data[month_name], pd.DataFrame([['', '', ''], ['', '', '']], columns=['', '', ''])],
                axis=1
            )

    combined_filename = os.path.join(settings.MEDIA_ROOT, 'csv_outputs', f'hourly_mean_{y_col}_all_months.csv')
    combined_data.to_csv(combined_filename, index=False)

    plt.tight_layout()
    plot_path = os.path.join(settings.MEDIA_ROOT, 'plots', 'plots.png')
    plt.savefig(plot_path)
    plt.close()

    return plot_path, combined_filename

def generate_yearly_mean_for_temp(dataframe):
    # Yearly mean for temperature
    dataframe = dataframe.dropna(subset=['TEMP(C)'])
    dataframe['YearMonth'] = dataframe['DATETIME'].dt.to_period('Y')
    yearly_mean_temp = dataframe.groupby('YearMonth')['TEMP(C)'].mean().reset_index()

    plt.figure(figsize=(10, 5))
    plt.plot(yearly_mean_temp['YearMonth'].dt.to_timestamp(), 
             yearly_mean_temp['TEMP(C)'], 
             marker='o', linestyle='-', color='b')
    plt.title('Yearly Mean Temperature')
    plt.xlabel('Year')
    plt.ylabel('Mean Temperature (°C)')
    plt.grid(True)
    plot_path = os.path.join(settings.MEDIA_ROOT, 'plots', 'yearly_mean_temp.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

def generate_yearly_mean_for_max_daily_temp(dataframe):
    # Yearly mean for max daily temperature
    dataframe = dataframe.dropna(subset=['TEMP_MAX(C)'])
    dataframe.set_index('DATETIME', inplace=True)
    daily_max_temp = dataframe['TEMP_MAX(C)'].resample('D').max()
    monthly_mean_max_temp = daily_max_temp.resample('M').mean()

    plt.figure(figsize=(10, 5))
    plt.plot(monthly_mean_max_temp.index, 
             monthly_mean_max_temp.values, 
             marker='o', linestyle='-', color='b')
    plt.title('Mean of Maximum Daily Temperature per Month')
    plt.xlabel('Month')
    plt.ylabel('Mean Maximum Temperature (°C)')
    plt.grid(True)
    plot_path = os.path.join(settings.MEDIA_ROOT, 'plots', 'yearly_mean_max_daily_temp.png')
    plt.savefig(plot_path)
    plt.close()
    return plot_path

def generate_daily_max_temp(dataframe):
    # Daily maximum temperature
    dataframe['YEAR'] = dataframe['DATETIME'].dt.year
    dataframe['MONTH'] = dataframe['DATETIME'].dt.month
    dataframe['DAY'] = dataframe['DATETIME'].dt.day
    dataframe = dataframe[dataframe['YEAR'] != 2021]
    daily_max_temps = dataframe.groupby(['YEAR', 'MONTH', 'DAY'])['TEMP(C)'].max().reset_index()
    daily_max_temps.rename(columns={'TEMP(C)': 'MAX_TEMP'}, inplace=True)
    years = daily_max_temps['YEAR'].unique()
    months = daily_max_temps['MONTH'].unique()
    month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                   5: 'May', 6: 'June', 7: 'July', 8: 'August', 
                   9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    
    plot_paths=[]

    for year in sorted(years):
        fig, axs = plt.subplots(6, 2, figsize=(15, 25), sharey=True)
        fig.suptitle(f'Daily Maximum Temperatures for {year}', fontsize=16)
        axs = axs.flatten()
        for i, month in enumerate(sorted(months)):
            ax = axs[i]
            monthly_data = daily_max_temps[(daily_max_temps['YEAR'] == year) & 
                                            (daily_max_temps['MONTH'] == month)]
            if not monthly_data.empty:
                sns.lineplot(data=monthly_data, x='DAY', y='MAX_TEMP', marker='o', ax=ax)
            ax.set_title(month_names[month])
            ax.set_xlabel('Day of the Month')
            ax.set_ylabel('Temperature (°C)')
            ax.grid(True)
        for i in range(len(months), len(axs)):
            fig.delaxes(axs[i])
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plot_path = os.path.join(settings.MEDIA_ROOT, 'plots', f'daily_max_temperatures_{year}.png')
        plt.savefig(plot_path)
        plt.close()
        plot_paths.append(plot_path)
    return plot_paths

def generate_wind_rose(dataframe):
    # Wind rose graph
    dataframe['Month'] = dataframe['DATETIME'].dt.month
    wind_speed = dataframe['WIND_SPEED(kt)']
    wind_direction = dataframe['WIND_DIR(deg)']
    months = range(1, 13)
    month_names = [calendar.month_name[month] for month in months]

    plot_paths=[]

    for month, month_name in zip(months, month_names):
        monthly_data = dataframe[dataframe['Month'] == month]
        if not monthly_data.empty:
            ax = WindroseAxes.from_ax()
            ax.bar(monthly_data['WIND_DIR(deg)'], monthly_data['WIND_SPEED(kt)'], 
                   normed=True, opening=0.8, edgecolor='white', cmap=viridis)
            ax.set_title(f'{month_name}')
            ax.legend(loc='lower right', bbox_to_anchor=(1.12, 0), fontsize=8)
            ax.set_rmax(20)
            ax.set_yticks(range(0, 21, 5))
            ax.set_yticklabels([str(i) for i in range(0, 21, 5)])
            plot_path = os.path.join(settings.MEDIA_ROOT, 'plots', f'wind_rose_{month_name}.png')
            plt.savefig(plot_path)
            plt.close()
            plot_paths.append(plot_path)
    
    return plot_paths

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            dataframe, columns = process_file(file_path)
            request.session['file_path'] = file_path
            request.session['columns'] = columns
            return redirect('select_graph_type')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def select_columns(request):
    columns = request.session.get('columns', [])
    file_path = request.session.get('file_path', '')
    if request.method == 'POST':
        form = SelectColumnForm(request.POST)
        form.fields['y_axis'].choices = [(col, col) for col in columns]
        if form.is_valid():
            y_axis = form.cleaned_data['y_axis']
            dataframe, _ = process_file(file_path)
            plot_path, csv_path = generate_plots_and_csv(dataframe, y_axis)
            request.session['plot_paths'] = [plot_path]
            request.session['csv_path'] = csv_path
            return redirect('results')
    else:
        form = SelectColumnForm()
        form.fields['y_axis'].choices = [(col, col) for col in columns]
    return render(request, 'select_columns.html', {'form': form, 'file_path': file_path})

def results(request):
    plot_paths = request.session.get('plot_paths', [])
    csv_path = request.session.get('csv_path', '')
    plot_urls=[]
    download_urls=[]

    if plot_paths:
        for path in plot_paths:
            plot_url = path.replace(settings.MEDIA_ROOT, settings.MEDIA_URL)
            download_url = reverse('download_image', kwargs={'filename': os.path.basename(path)})
            plot_urls.append(plot_url)
            download_urls.append(download_url)

    csv_url=csv_path.replace(settings.MEDIA_ROOT,settings.MEDIA_URL)if csv_path else None
    download_csv_url = reverse('download_file', kwargs={'filename': os.path.basename(csv_path)}) if csv_path else None

    context = {
        'plot_data': zip(plot_urls, download_urls), 
        'csv_url': csv_url,
        'download_csv_url': download_csv_url
    }
    graph_type = request.session.get('graph_type', '')

    if graph_type == 'wind_rose':
        return render(request, 'results_windrose.html', context)
    else:
        return render(request, 'results.html', context)


def download_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'csv_outputs', filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
            return response
    else:
        return HttpResponse("File not found.")
    
def download_image(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'plots', filename)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse("File not found.")

def about(request):
    return render(request, 'about.html')

def team(request):
    return render(request, 'team.html')