from datetime import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from googleAPI.models import NotificationQueue, Record
import urllib.request
import telebot
from googleapiclient.discovery import build
from django.conf import settings
from channels.db import database_sync_to_async


class DatabaseConsumer(AsyncJsonWebsocketConsumer):
    async def receive_json(self, content):
        
        command = content.get("command", None)
        try:
            if command == "table_update":
                is_updated = await table_update()# Обновляем данные бд
                if is_updated:
                    await self.update_page() # Если в бд произошли изменения, обновляем страницу
                else:
                    await self.refresh_json() # Если нет, то снова проверяем наличие изменений в таблице
        except Exception as e:
            print(e)

    async def update_page(self):
        await self.send_json(
            {
                "update_page": True
            },
        )
    async def refresh_json(self):
        true = True
        await self.send_json(
            {
                "refresh_json": True
            },
        )
    

@database_sync_to_async
def table_update():
    print('table is updating...')
    try:
        service = build('sheets', 'v4', credentials=settings.CREDENTIALS)
        search_range = 'Sheet1!A2:D999'
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=settings.SAMPLE_SPREADSHEET_ID, range=search_range).execute()
        values = result.get('values') 

        # Получаем курс доллара на сегодняшний день 
        url = "http://www.cbr.ru/scripts/XML_daily.asp" 
        data = urllib.request.urlopen(url)
        data = str(data.read())
        temp = data.find('USD') 
        left = data.find('</Value>',temp)
        right = data.find('<Value>',temp)+7
        dollar = float(data[right:left].replace(',','.'))

        db_updated = False

        to_delete = []
        for i in Record.objects.all():
            to_delete.append(i.table_number)
            
        # Работа с бд
        for i in values:
            
            delivery_date = datetime.date(datetime(int(i[3][6:]), int(i[3][3:5]), int(i[3][:2])))
            
            # Создаем эллемент, отсутствующий в бд
            if not Record.objects.filter(table_number=int(i[0])):
                db_updated = True
                record = Record(
                    table_number = int(i[0]),
                    order_number = int(i[1]),
                    price = int(i[2]),
                    price_rubles = int(i[2])*dollar,
                    delivery_date = delivery_date)
                record.save()
                notification = NotificationQueue(record_identifier=record, delivery_date=delivery_date)
                notification.save()

            # Проверяем наличие изменений в существующем элементе 
            else:
                record = Record.objects.get(table_number=int(i[0]))
                to_delete.pop(to_delete.index(int(i[0])))
                if record.order_number != int(i[1]):
                    db_updated = True
                    record.order_number = int(i[1])
                if record.price != int(i[2]):
                    db_updated = True
                    record.price = int(i[2])
                    record.price_rubles = int(i[2])*dollar
                if record.delivery_date != delivery_date:
                    db_updated = True
                    notification = NotificationQueue.objects.get(record_identifier=record)
                    notification.delivery_date = delivery_date
                    notification.is_worked_out = False
                    notification.save()
                    record.delivery_date = delivery_date
                record.save()

        # Удаляем лишние элементы
        for i in to_delete:
            db_updated = True
            el = Record.objects.get(table_number=i)
            el.delete()
            

        # Проверяем необходимость напомнить о сроке поставки
        if str(datetime.now().time())[0:5]==settings.NOTIFICATION_TIME:
            notifications = NotificationQueue.objects.filter(delivery_date=datetime.date(datetime.now()), is_worked_out=False)

            # Отправляем сообщение, если такая необходимость присутствует
            if notifications:
                temp = []
                for notification in notifications:
                    temp.append(str(notification.record_identifier.order_number))
                    notification.is_worked_out = True
                    notification.save()
                if len(temp)==1:
                    TEXT = f"На сегодняшний день назначена поставка, номер заказа: {temp[0]}."
                else: 
                    TEXT = "На сегодняшний день назначены поставки, номера заказов: "+", ".join(temp)+"."

                bot = telebot.TeleBot(settings.TOKEN_API)
                bot.send_message(settings.TELEGRAM_ID, TEXT)
                print(f"Сообщение: {TEXT} успешно отправлено!")
        

        # Обновляем данные страницы, если база данных была обновлена
        print('changes', db_updated)
        if db_updated:
            return True
        return
    except Exception as e:
        print(e)
        return False
