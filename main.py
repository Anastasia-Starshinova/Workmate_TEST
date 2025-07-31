import argparse
import json
from tabulate import tabulate


def parse_file(filepath):
    count_requests = {}
    # считаем количество запросов по каждому эндпоинту
    all_response_time = {}
    # записываем общее время по каждому эндпоинту

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                log = json.loads(line)
                url = log.get('url')
                response_time = log.get('response_time')

                if url is None or response_time is None:
                    continue

                if url not in count_requests:
                    count_requests[url] = 1
                else:
                    count_requests[url] += 1

                if url not in all_response_time:
                    all_response_time[url] = response_time
                else:
                    all_response_time[url] += response_time

            except json.JSONDecodeError:
                continue

    average_response_time = {}
    for url in all_response_time:
        count = count_requests[url]
        all_time = all_response_time[url]
        answer = all_time / count
        average_response_time[url] = answer

    count_requests_and_average_time = {}
    # финальный словарь со всеми данными

    for url in count_requests:
        count_and_time = {'count': count_requests.get(url), 'time': average_response_time.get(url)}
        count_requests_and_average_time[url] = count_and_time

    return count_requests_and_average_time


def print_report(final_data):
    list_url = list(final_data.keys())
    table_data = []

    for url, data in final_data.items():
        table_data.append([url, data['count'], data['time']])

    headers = ['endpoint', 'count', 'medium time (sec)']
    table = tabulate(table_data, headers=headers, tablefmt='grid')
    # выводим отчет в консоль
    print('\nСписок всех эндпоинтов:')
    print(list_url)
    print('\nОтчёт:')
    print(table)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='Путь к лог-файлу')

    args = parser.parse_args()

    report = parse_file(args.file)
    print_report(report)

