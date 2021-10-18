import time
# from okex import OkEx
from OkcoinFutureAPI import OKCoinFuture
import requests
import json
import re
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import numpy as np

access_key = 'your-access-key'
secret_key = 'your-secret-key'

url = 'https://www.okex.com'
slippage_fee = 0.0002
taker_fee = 0.0003
maker_fee = 0.0001
okcoinFuture = OKCoinFuture(url,access_key,secret_key)


def get_future_quarter_close_price(trade_token):
    """

    Get the quarter future trade token's close price.

    :param trade_token:
    :return:
    """
    info_url = 'https://www.okex.com/api/v1/future_ticker.do?symbol=%s&contract_type=quarter' % trade_token
    info_url_content = requests.get(info_url).content
    price_data = json.loads(info_url_content)
    close_price = price_data['ticker']['last']
    print('\033[0;32;40m\tThe %s close price is:\033[0m \033[0;31;40m\t%s\033[0m' % (trade_token,close_price))
    return close_price


def get_account_balance(token):
    """

    Get your account's balance.

    :param token:
    :return:
    """
    user_info = okcoinFuture.future_userinfo()
    data = json.loads(user_info)
    holder_balance = data['info'][token]['account_rights']
    print('\033[0;32;40m\tYour %s balance is:\033[0m \033[0;31;40m\t%s\033[0m'%(token,holder_balance))
    return holder_balance


def get_holder_info(trade_token):
    """

    Get your quarter future holding info.
    lever rate is 10x or 20x.
    contract type is this week, next week or quarter.
    buy/sell amount is your order direction's holding.
    buy/sell price average is your order average price.
    buy/sell available is your order average buy/sell amount.

    :param trade_token:
    :return:
    """
    user_holder_info = okcoinFuture.future_position(trade_token,'quarter')
    holding_profit_all_data = json.loads(user_holder_info)
    holding_profit_data = holding_profit_all_data['holding']
    holding_force_price = holding_profit_all_data['force_liqu_price']
    for holding_details in holding_profit_data:
        if direction is '1':
            order_avg_price = holding_details['buy_price_avg']
            order_holding_amount = holding_details['buy_amount']
            order_available_amount = holding_details['buy_available']
        elif direction is '2':
            order_avg_price = holding_details['sell_price_avg']
            order_holding_amount = holding_details['sell_amount']
            order_available_amount = holding_details['sell_available']
    # print(holding_details)
    print('\033[0;32;40m\tYour holding average price is:\033[0m \033[0;31;40m\t{0:*^30}\033[0m'.format(order_avg_price))
    print('\033[0;32;40m\tYour holding amount is:\033[0m \033[0;31;40m\t{0:*^30}\033[0m'.format(order_holding_amount))
    print('\033[0;32;40m\tYour available amount is:\033[0m \033[0;31;40m\t{0:*^30}\033[0m'.format(order_available_amount))
    print('\033[0;32;40m\tYour force liquidation price is:\033[0m \033[0;31;40m\t{0:*^30}\033[0m'.format(holding_force_price))
    print('')
    return order_avg_price,order_holding_amount,order_available_amount


def calculate_profit(open_order_price,close_price,direction,margin):
    """

    Calculate your holding profit and profit percent.

    :param open_order_price:
    :param close_price:
    :param direction:
    :param margin:
    :return:
    """
    if direction is '1':
        profit_meta = (close_price - open_order_price) / open_order_price
        profit = profit_meta * 20 * float(margin)
        profit_percent = profit / float(margin) * 100
        print('\033[0;32;40m\tYour profit is:\033[0m \033[0;31;40m\t%.5f\033[0m' % profit)
        print('\033[0;32;40m\tYour profit percent is:\033[0m \033[0;31;40m\t%.3f%%\033[0m' % profit_percent)
    elif direction is '2':
        profit_meta = (open_order_price - close_price) / close_price
        profit = profit_meta * 20 * float(margin)
        profit_percent = profit / float(margin) * 100
        print('\033[0;32;40m\tYour profit is:\033[0m \033[0;31;40m\t%.5f\033[0m' % profit)
        print('\033[0;32;40m\tYour profit percent is:\033[0m \033[0;31;40m\t%.3f%%\033[0m' % profit_percent)
    return profit,profit_percent


def get_future_position(trade_token):
    """

    Get all your holding position.

    :param trade_token:
    :return:
    """
    future_position = okcoinFuture.future_position(trade_token,'quarter')
    print(future_position)


def future_order(trade_token,order_price,order_amount,order_type):
    """

    Make quarter future order.order type is: 1：开多 2：开空 3：平多 4：平空

    :param trade_token:
    :param order_price:
    :param order_amount:
    :param trade_type:
    :return:
    """
    order_future = okcoinFuture.future_trade(trade_token,'quarter',order_price,order_amount,order_type,'0','20')
    order_details = json.loads(order_future)
    order_id = order_details['order_id']
    print(order_future)
    print(order_id)
    return order_id


def order_close(trade_token,order_price,order_amount,direction):
    """

    Close your holding. order type is: 1：开多 2：开空 3：平多 4：平空

    :param trade_token:
    :param order_price:
    :param order_amount:
    :param direction:
    :return:
    """
    order_future = okcoinFuture.future_trade(trade_token, 'quarter', order_price, order_amount, direction, '0', '20')
    order_details = json.loads(order_future)
    if order_details['result'] is True:
        print('Close order is OK.')
    else:
        print('I got an Error!')
    print(order_future)
    print(order_details['result'])


def order_cancel(trade_token,order_id):
    """

    Cancel the special id order.

    :param trade_token:
    :param order_id:
    :return:
    """
    cancel_order = okcoinFuture.future_cancel(trade_token,'quarter',order_id)
    print(cancel_order)


# def save_to_file(get_time,EOS_balance,ADD_balance,bid_avg_cost,delivery_price,auto_volume):
#     """
#
#     save the param to csv file, include get_time, EOS_balance, ADD_balance, bid_avg_cost, delivery_price and auto_volume.
#
#     :param get_time:
#     :param EOS_balance:
#     :param ADD_balance:
#     :param bid_avg_cost:
#     :param delivery_price:
#     :param auto_volume:
#     :return:
#     """
#     with open('bid_avg_cost.csv','a',) as f:
#         fieldnames = ['Run_Time','EOS_Balance','ADD_Balance','Bid_Avg_Cost','Delivery_Price','Auto_Volume']
#         writer = csv.DictWriter(f,fieldnames=fieldnames)
#         if os.path.getsize('bid_avg_cost.csv') == 0:
#             writer.writeheader()
#         writer.writerow({'Run_Time':get_time,'EOS_Balance':EOS_balance,'ADD_Balance':ADD_balance,
#                          'Bid_Avg_Cost':bid_avg_cost,'Delivery_Price':delivery_price,'Auto_Volume':auto_volume})
#         f.close()


def alarm_send_email(email_content):
    """

    send the alarm email.

    :param email_content:
    :return:
    """
    host_server = 'smtp.163.com'
    sender = 'your-email'
    receiver = 'receiver-email'
    sender_passwd = 'your-email-password'
    # email_content = "Hi, <p>Your script is stopping...</p>"
    email_title = 'Bot Alarming~'
    smtp = SMTP_SSL(host_server)
    smtp.set_debuglevel(1)
    smtp.ehlo(host_server)
    smtp.login(sender,sender_passwd)
    msg = MIMEText(email_content, "html", 'utf-8')
    msg['Subject'] = Header(email_title, 'utf-8')
    msg['From'] = sender
    msg['To'] = Header("Lei", 'utf-8')
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()


if __name__ == '__main__':
    # token = input('Please input your tarde token:\n')
    # order_price = input('Please input your order price:\n')
    # order_amount = input('Please input your order amount:\n')
    token = 'btc'
    print('Your trade token is BTC......')
    print('')
    direction = input('Please select your order direction just now:\n 1：开多 2：开空 3：平多 4：平空\n')
    trade_token = token + '_usd'
    margin = input('Please watch your margin:\n')
    positive_profit_list = []
    negative_profit_list = []
    positive_price_list = []
    negative_price_list = []
    pos_retrace_profit_list = []
    neg_retrace_profit_list =[]
    pos_retrace_price_list = []
    neg_trace_price_list = []
    pos_avg_price = []
    neg_avg_price = []
    pos_avg_profit = []
    neg_avg_profit = []
    i = 0
    # base_profit_percent = 7
    # print('base_percent is {}'.format(base_profit_percent))
    while True:
        close_price = get_future_quarter_close_price(trade_token)
        open_order_price,all_amount,available_order_amount = get_holder_info(trade_token)
        profit_meta,profit_percent_meta = calculate_profit(open_order_price,close_price,direction,margin)
        profit = round(profit_meta,5)
        profit_percent = round(profit_percent_meta,3)
        # base_profit_percent = 7
        # print('base_percent is {}'.format(base_profit_percent))
        if profit_percent > 7 and len(positive_profit_list) > 0:
            print('+profit and != None')
            print('positive is {}'.format(positive_profit_list))
            pos_list_max_profit = positive_profit_list[0]
            pos_list_max_price = positive_price_list[0]
            pos_retrace_profit = pos_list_max_profit * 0.63
            pos_retrace_price = pos_list_max_price * 0.63
            if profit_percent > pos_list_max_profit:
                positive_profit_list.append(profit_percent)
                positive_profit_list.sort(reverse=True)
                pos_list_max_profit = positive_profit_list[0]
                pos_retrace_profit = pos_list_max_profit * 0.63
                pos_retrace_profit_list.append(pos_retrace_profit)
                positive_price_list.append(close_price)
                positive_price_list.sort(reverse=True)
                pos_list_max_price = positive_price_list[0]
                pos_retrace_price = pos_list_max_price * 0.63
                pos_retrace_price_list.append(pos_retrace_price)
                print('profit_percent > poos_list_max_profit')
            elif pos_retrace_profit <= profit_percent <= positive_profit_list[0]:
                    pos_avg_profit.append(profit_percent)
                    pos_avg_price.append(close_price)
                    print('pos_retrace_profit <= profit_percent <= pos_list_max_profit')
                    print('pos_avg_profit list is {}'.format(pos_avg_profit))
                    print('pos_avg_price list is {}'.format(pos_avg_price))
                    i = i + 1
                    if i == 4:
                        pos_avg_order_profit = round(np.mean(pos_avg_profit),3)
                        pos_avg_order_price = round(np.mean(pos_avg_price), 3)
                        order_close(trade_token, pos_avg_order_price, available_order_amount, int(direction) + 2)
                        message = 'Your order profit percent is %s%%, order profit is %s and I close the order......' % (
                        pos_avg_order_profit, profit)
                        print(alarm_send_email(message))
                        print('pos_retrace_profit <= profit_percent <= pos_list_max_profit')
                        print('pos_avg_order_profit is {}'.format(pos_avg_order_profit))
                        print('pos_avg_order_price is {}'.format(pos_avg_order_price))
                        print('pos_avg_price_list is {}'.format(pos_avg_price))
                        print(i)
                        # pos_avg_profit.clear()
                        # pos_avg_price.clear()
                        # i = 0
                        break
                        # if pos_avg_order_profit != base_profit_percent:
                        #     base_profit_percent = pos_avg_order_profit
                        # elif pos_avg_order_profit == base_profit_percent:
                        #     pos_avg_order_price = round(np.mean(pos_avg_price),3)
                        #     order_close(trade_token, pos_avg_order_price, available_order_amount, int(direction)+2)
                        #     message = 'Your order profit percent is %s%%, order profit is %s and I close the order......' % (pos_avg_order_profit,profit)
                        #     print(alarm_send_email(message))
                        #     print('pos_retrace_profit <= profit_percent <= pos_list_max_profit')
                        #     print('pos_avg_order_profit is {}'.format(pos_avg_order_profit))
                        #     print('pos_avg_order_price is {}'.format(pos_avg_order_price))
                        #     print('pos_avg_price_list is {}'.format(pos_avg_price))
                        #     print(i)
                        #     pos_avg_profit.clear()
                        #     pos_avg_price.clear()
                        #     i = 0
                        #     break
            elif profit_percent < pos_retrace_profit:
                i = i + 1
                if i == 4:
                    pos_order_profit = pos_retrace_profit
                    pos_order_price = pos_retrace_price
                    print('profit_percent < pos_retrace_profit')
                    print('pos_retrace_price is {}'.format(pos_order_price))
                    order_close(trade_token, pos_order_price, available_order_amount, int(direction)+2)
                    message = 'Your order profit percent is %s%%, order prifit is %s and I close the order......' % (pos_order_profit, profit)
                    print(alarm_send_email(message))
                    break
            print(positive_profit_list)
            print(pos_list_max_profit)
            print(pos_retrace_profit)
            time.sleep(10)
        elif profit_percent > 7 and len(positive_profit_list)<=0:
            print('+profit and is None')
            positive_profit_list.append(profit_percent)
            positive_price_list.append(close_price)
            print(positive_profit_list)
            print('positive_price_list is {}'.format(positive_price_list))
            time.sleep(3)
        elif profit_percent < -5 and len(negative_profit_list) > 0:
            print('-profit and != None')
            print('negative is {}'.format(negative_profit_list))
            neg_list_max_profit = negative_profit_list[0]
            neg_list_max_price = negative_price_list[0]
            neg_retrace_profit = -37
            neg_retrace_price = open_order_price * 0.63
            if profit_percent <= -37:
                i = i + 1
                if i == 4:
                    neg_order_profit = neg_retrace_profit
                    neg_order_price = neg_retrace_price
                    print('profit_percent <= neg_retrace_profit')
                    order_close(trade_token, neg_order_price, available_order_amount, int(direction)+2)
                    message = 'Your order profit percent is %s%%, order profit is %s and I close the order......' % (neg_order_profit, profit)
                    print(alarm_send_email(message))
                    break
            elif -37 < profit_percent < -5:
                neg_avg_profit.append(profit_percent)
                neg_avg_price.append(close_price)
                i = i + 1
                if i == 4:
                    neg_avg_order_profit = round(np.mean(neg_avg_profit), 3)
                    neg_avg_order_price = round(np.mean(neg_avg_price),3)
                    print('-37 < profit_percent < -3')
                    print(neg_avg_order_profit)
                    print('neg_avg_price_list is {}'.format(neg_avg_price))
                    print(i)
                    order_close(trade_token, neg_avg_order_price, available_order_amount, int(direction)+2)
                    message = 'Your order profit percent is %s%%, order profit is %s and I close the order......' % (neg_avg_order_profit, profit)
                    print(alarm_send_email(message))
                    break
                # negative_profit_list.append(profit_percent)
                # negative_profit_list.sort(reverse=True)
                # neg_list_max_list = negative_profit_list[0]
            print(negative_profit_list)
            print(neg_list_max_profit)
            print(neg_avg_price)
            time.sleep(10)
        elif profit_percent < -5 and len(negative_profit_list) <= 0:
            print('-profit and is None')
            negative_profit_list.append(profit_percent)
            negative_price_list.append(close_price)
            print(negative_profit_list)
            time.sleep(3)
        time.sleep(4)

