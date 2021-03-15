
import requests
import time


def get_balance_change_by_user(block_tag):
    """
    str block_tag
    Выберем всех пользователей, чей баланс изменился за блок
    :return: dict вида
    {
        'username1': change,
        'username2': change,
        ...
        ...
        ...
    },
    где change может быть как + так и - к балансу
    """
    link = 'https://api.etherscan.io/api?module=proxy&action=eth_getBlockByNumber&tag={}&boolean=true'.format(block_tag)
    request = requests.get(link)
    if request.status_code != 200:
        return 0
    data = request.json()
    transactions = data['result']['transactions']  # получили список транзакций
    result = {}
    for transaction in transactions:
        transfer_value = int(transaction['value'], 16)
        if transaction['from'] in result.keys():
            result[transaction['from']] -= transfer_value
        else:
            result[transaction['from']] = -transfer_value
        # баланс отправителя изменился
        if transaction['to'] in result.keys():
            result[transaction['to']] += transfer_value
        else:
            result[transaction['to']] = transfer_value
    return result


def get_last_block_tag():
    """
    Найдем тег последнего блока
    :return: int номер блока
    """
    request = requests.get('https://api.etherscan.io/api?module=proxy&action=eth_blockNumber').json()
    last_block_tag = request['result']  # Поверим что всегда болучим валидный тег
    last_block_number = int(last_block_tag, 16)
    return last_block_number


def complete_calculation(last_block_number):
    """
    int last_block_number
    Закидываем номер последнего блока и собираем данные по сотне блоков выше
    :return: str идентификатор пользователя с самым большим изменением
    """
    pre_result = []
    for block_number in range(last_block_number-99, last_block_number+1):
        data = get_balance_change_by_user(str(hex(block_number)))
        pre_result.append(data)
        time.sleep(5)
    total_balance = {}
    for user_balance_change_block in pre_result:
        for user_tag in user_balance_change_block:
            if user_tag in total_balance:
                total_balance[user_tag] += user_balance_change_block[user_tag]
            else:
                total_balance[user_tag] = user_balance_change_block[user_tag]
    most_changed_balance_user_tag = list(total_balance.keys())[list(total_balance.values()).index(max(total_balance.values()))]
    return most_changed_balance_user_tag


last_block = get_last_block_tag()
time.sleep(5)
print(complete_calculation(last_block))
