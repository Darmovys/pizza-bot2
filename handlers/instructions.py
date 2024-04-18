import os
from typing import Any
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, on
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from utils.functions import (get_pizzas, file_exists,
                             insert_object, update_pizza_title, update_pizza_types, delete_pizza_size,
                             insert_pizza_size, update_pizza_size, update_pizza_price, update_pizza_photo,
                             delete_pizza)
from keyboards import main, add_pizza, change_pizza
from utils.states import StartStatus, SendData

types = ["тонка", "традиційна"]

TOKEN = "Insert your token API"
CODE = "supersecretpassword"
CHANNEL_FOR_RECEIVING_ORDERS = "Insert your channel ID"

bot = Bot(TOKEN)


class ChangePizzaPhoto(Scene, state="change_pizza_photo"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        await state.update_data(imageUrl=pizza["imageUrl"])
        await message.reply_photo(
            photo=FSInputFile(
                path=pizza["imageUrl"]
            ),
            caption=f'Відправте нову картинку як файл. 👇',
            reply_markup=ReplyKeyboardRemove()
        )

    @on.message(F.document)
    async def upload_file(self, message: Message, state: FSMContext) -> Any:
        if file_exists(message.document.file_name):
            await message.answer("Файл з такою назвою вже присутній в базі даних.")
        else:
            data = await state.get_data()
            pizza_id = data["pizza_id"]
            step = data["step"]
            image_url = data["imageUrl"]
            os.remove(image_url)
            file_name = f"./static/Img/{message.document.file_name}"
            await bot.download(message.document, destination=file_name)
            update_pizza_photo(pizza_id, file_name)
            await message.answer("Картинку додано.")
            return await self.wizard.goto(ChangePizza, step=step)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда")


class ChangePizzaPrice(Scene, state="change_pizza_price"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        await message.reply_photo(
            photo=FSInputFile(
                path=pizza["imageUrl"]
            ),
            caption=f'Ціна – {pizza["price"]} грн. за мінімальний розмір\n\nВведіть нову ціну 👇',
            reply_markup=ReplyKeyboardRemove()
        )

    @on.message(F.text)
    async def change_price(self, message: Message, state: FSMContext) -> Any:
        if message.text.isdigit():
            data = await state.get_data()
            pizza_id = data["pizza_id"]
            step = data["step"]
            update_pizza_price(pizza_id, int(message.text))
            await message.answer("Ціну змінено.")
            return await self.wizard.goto(ChangePizza, step=step)
        else:
            await message.answer("Невірний формат")

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда")


class UpdatePizzaSize(Scene, state="update_pizza_size"):
    sizes = []

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        CheckPizzaSize.sizes = pizza["sizes"]
        await message.answer(
            text="Введіть новий розмір",
            reply_markup=ReplyKeyboardRemove()
        )

    @on.message(F.text)
    async def change_size(self, message: Message, state: FSMContext) -> Any:
        if message.text.isdigit():
            msg = int(message.text)
            if msg in CheckPizzaSize.sizes:
                await message.answer(text="Такий розмір вже є")
            else:
                if msg < 27:
                    await message.answer(text="Новий розмір повинен бути не менше 27 см.")
                else:
                    data = await state.get_data()
                    pizza_id = data["pizza_id"]
                    selected_size = data["selected_size"]
                    update_pizza_size(pizza_id, selected_size, msg)
                    await message.answer("Розмір змінено")
                    return await self.wizard.goto(ChangePizzaSizes)
        else:
            await message.answer("Невірний формат")

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class CheckPizzaSize(Scene, state="check_pizza_size"):
    sizes = []

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        CheckPizzaSize.sizes = pizza["sizes"]
        markup = ReplyKeyboardBuilder()
        for i in pizza["sizes"]:
            if i == 26:
                continue
            else:
                markup.button(text=str(i))

        await message.answer(
            text="Виберіть розмір який ви хочете змінити.",
            reply_markup=markup.adjust(2).as_markup(resize_keyboard=True)
        )

    @on.message(F.text)
    async def choose_size(self, message: Message, state: FSMContext) -> Any:
        if message.text.isdigit():
            msg = int(message.text)
            if msg in CheckPizzaSize.sizes:
                if msg != 26:
                    index = CheckPizzaSize.sizes.index(msg)
                    await state.update_data(selected_size=index)
                    return await self.wizard.goto(UpdatePizzaSize)
                else:
                    await message.answer("Неможливо змінити мінімальне значення")
            else:
                await message.answer("Такого розміру немає")
        else:
            await message.answer("Такого розміру немає")

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class AddNewPizzaSize(Scene, state="add_new_pizza_size"):
    sizes = []

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        AddNewPizzaSize.sizes = pizza["sizes"]
        await message.answer(text="Введіть новий розмір (не менше 27 см)", reply_markup=ReplyKeyboardRemove())

    @on.message(F.text)
    async def add_new_size(self, message: Message, state: FSMContext) -> Any:
        if message.text.isdigit():
            msg = int(message.text)
            if msg in AddNewPizzaSize.sizes:
                await message.answer(text="Такий розмір вже є")
            else:
                if msg < 27:
                    await message.answer(text="Розмір повинен бути не менше 27 см")
                else:
                    data = await state.get_data()
                    pizza_id = data["pizza_id"]
                    insert_pizza_size(pizza_id, msg)
                    await message.answer(text="Розмір додано")
                    return await self.wizard.goto(ChangePizzaSizes)
        else:
            await message.answer(text="Невірний ввід")

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class DeletePizzaSize(Scene, state="delete_pizza_size"):
    sizes = []

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        DeletePizzaSize.sizes = pizza["sizes"]
        markup = ReplyKeyboardBuilder()
        for i in pizza["sizes"]:
            if i == 26:
                continue
            else:
                markup.button(text=str(i))

        await message.answer(
            text="Виберіть розмір який ви хочете видалити.",
            reply_markup=markup.adjust(2).as_markup(resize_keyboard=True)
        )

    @on.message(F.text)
    async def delete_size(self, message: Message, state: FSMContext) -> Any:
        if message.text.isdigit():
            msg = int(message.text)
            if msg in DeletePizzaSize.sizes:
                if msg != 26:
                    data = await state.update_data()
                    pizza_id = data["pizza_id"]
                    delete_pizza_size(pizza_id, msg)
                    await message.answer(f"Розмір {msg} видалено")
                    return await self.wizard.goto(ChangePizzaSizes)
                else:
                    await message.answer("Неможливо видалити мінімальне значення")
            else:
                await message.answer("Такого розміру немає")
        else:
            await message.answer("Такого розміру немає")

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class ChangePizzaSizes(Scene, state="change_pizza_sizes"):
    sizes_p = []

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:

        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        ChangePizzaSizes.sizes_p = pizza["sizes"]
        pizza_sizes = ""
        markup = ReplyKeyboardBuilder()
        markup.button(text="Видалити розмір")
        markup.button(text="Додати розмір")
        markup.button(text="Змінити розмір")
        markup.button(text="✔ Готово")
        for size in pizza["sizes"]:
            pizza_sizes += str(size) + ", "
        await message.reply_photo(
            photo=FSInputFile(
                path=pizza["imageUrl"]
            ),
            caption=f"Розміри – {pizza_sizes[:-2]}\n\nВиберіть опцію",
            reply_markup=markup.adjust(3, 1).as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "Видалити розмір")
    async def delete_size(self, message: Message) -> Any:
        if len(ChangePizzaSizes.sizes_p) == 1:
            await message.answer("Неможливо видалити мінімальне значення")
        else:
            await self.wizard.goto(DeletePizzaSize)

    @on.message(F.text == "Додати розмір")
    async def add_size(self, message: Message) -> Any:
        if len(ChangePizzaSizes.sizes_p) <= 3:
            await self.wizard.goto(AddNewPizzaSize)
        else:
            await message.answer("Неможливо додати більше 4-х розмірів")

    @on.message(F.text == "Змінити розмір")
    async def change_size(self, message: Message) -> Any:
        if len(ChangePizzaSizes.sizes_p) == 1:
            await message.answer("Неможливо змінити мінімальне значення")
        else:
            await self.wizard.goto(CheckPizzaSize)

    @on.message(F.text == "✔ Готово")
    async def done(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        step = data["step"]
        return await self.wizard.goto(ChangePizza, step=step)

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class ChangePizzaTypes(Scene, state="change_pizza_types"):
    thin = bool
    traditional = bool
    both = bool

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        ChangePizzaTypes.thin = True
        ChangePizzaTypes.traditional = True
        ChangePizzaTypes.both = True
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        types_i = pizza["types"]
        pizza_types = ""
        for i in types_i:
            pizza_types += types[i] + ", "
        markup = ReplyKeyboardBuilder()
        if 0 in types_i and 1 in types_i:
            markup.button(text="Тонка")
            markup.button(text="Традиційна")
            ChangePizzaTypes.thin = False
            ChangePizzaTypes.traditional = False
        elif 0 in types_i:
            markup.button(text="Традиційна")
            markup.button(text="Тонка і традиційна")
            ChangePizzaTypes.traditional = False
            ChangePizzaTypes.both = False
        else:
            markup.button(text="Тонка")
            markup.button(text="Тонка і традиційна")
            ChangePizzaTypes.thin = False
            ChangePizzaTypes.both = False

        await message.reply_photo(
            photo=FSInputFile(
                path=pizza["imageUrl"]
            ),
            caption=f"Типи – {pizza_types[:-2]}\n\nЗамініть тип піци",
            reply_markup=markup.as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "Тонка")
    async def thin_type(self, message: Message, state: FSMContext) -> Any:
        if ChangePizzaTypes.thin:
            return await message.answer("Цей тип вже встановлено")
        data = await state.update_data()
        step = data["step"]
        pizza_id = data["pizza_id"]
        update_pizza_types(pizza_id, [0])
        await message.answer("Тип Змінено.")
        await self.wizard.goto(ChangePizza, step=step)

    @on.message(F.text == "Традиційна")
    async def traditional_type(self, message: Message, state: FSMContext) -> Any:
        if ChangePizzaTypes.traditional:
            return await message.answer("Цей тип вже встановлено")
        data = await state.update_data()
        step = data["step"]
        pizza_id = data["pizza_id"]
        update_pizza_types(pizza_id, [1])
        await message.answer("Тип Змінено.")
        await self.wizard.goto(ChangePizza, step=step)

    @on.message(F.text == "Тонка і традиційна")
    async def both_types(self, message: Message, state: FSMContext) -> Any:
        if ChangePizzaTypes.both:
            return await message.answer("Цей тип вже встановлено")
        data = await state.update_data()
        step = data["step"]
        pizza_id = data["pizza_id"]
        update_pizza_types(pizza_id, [0, 1])
        await message.answer("Тип Змінено.")
        await self.wizard.goto(ChangePizza, step=step)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class ChangePizzaTitle(Scene, state="change_pizza_title"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizzas = get_pizzas()
        pizza = pizzas[data["step"]]
        await message.reply_photo(
            photo=FSInputFile(
                path=pizza["imageUrl"]
            ),
            caption=f"{pizza['title']}\n\nВведіть нову назву 👇",
            reply_markup=ReplyKeyboardRemove()
        )

    @on.message(F.text)
    async def change_title(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizza_id = data["pizza_id"]
        step = data["step"]
        update_pizza_title(pizza_id, message.text)
        await message.answer("Назву змінено.")
        return await self.wizard.goto(ChangePizza, step=step)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда")


class ChangePizzaSelected(Scene, state="change_pizza_selected"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        await message.answer(text="Виберіть дію", reply_markup=change_pizza)

    @on.message(F.text == "Змінити назву")
    async def change_title(self, message: Message) -> Any:
        return await self.wizard.goto(ChangePizzaTitle)

    @on.message(F.text == "Змінити тип")
    async def change_type(self, message: Message) -> Any:
        return await self.wizard.goto(ChangePizzaTypes)

    @on.message(F.text == "Змінити розмір")
    async def change_size(self, message: Message) -> Any:
        return await self.wizard.goto(ChangePizzaSizes)

    @on.message(F.text == "Змінити ціну")
    async def change_price(self, message: Message) -> Any:
        return await self.wizard.goto(ChangePizzaPrice)

    @on.message(F.text == "Змінити картинку")
    async def change_picture(self, message: Message) -> Any:
        return await self.wizard.goto(ChangePizzaPhoto)

    @on.message(F.text == "❌ Видалити піцу")
    async def add_picture(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizza = data["pizza"]
        pizza_id = data["pizza_id"]
        image_url = pizza["imageUrl"]
        os.remove(image_url)
        delete_pizza(pizza_id)
        await message.answer(text="Піцу видалено")
        return await self.wizard.goto(ChangePizza)

    @on.message(F.text == "✔ Готово")
    async def done(self, message: Message, state: FSMContext) -> Any:
        data = await state.update_data()
        step = data["step"]
        return await self.wizard.goto(ChangePizza, step=step)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда")


class ChangePizza(Scene, state="change_pizza"):
    id = ''

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
        data = await state.get_data()
        if step is None:
            step = data["step"]
        pizzas = get_pizzas()
        p_len = len(pizzas)

        pizza = pizzas[step]

        ChangePizza.id = pizza["_id"]
        markup = ReplyKeyboardBuilder()
        markup.button(text="⚙ Змінити")
        if not step == p_len - 1:
            markup.button(text="➡ Далі")
        if step > 0:
            markup.button(text="⬅ Назад")
        markup.button(text="🚫 Вихід")

        await state.update_data(step=step)
        await state.update_data(pizza=pizza)
        types_i = pizza["types"]
        sizes = pizza["sizes"]
        pizza_types = ""
        pizza_sizes = ""
        for i in types_i:
            pizza_types += types[i] + ", "
        for size in sizes:
            pizza_sizes += str(size) + ", "

        await message.reply_photo(
            photo=FSInputFile(
                path=pizza["imageUrl"]
            ),
            caption=f'''
                {pizza["title"]}\n
                Ціна – {pizza["price"]} грн.\n
                Типи – {pizza_types[:-2]}\n
                Розміри – {pizza_sizes[:-2]} см.\n
            ''',
            reply_markup=markup.adjust(1, 2, 1).as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "⚙ Змінити")
    async def choose_pizza(self, message: Message, state: FSMContext) -> None:
        await state.update_data(pizza_id=ChangePizza.id)
        return await self.wizard.goto(ChangePizzaSelected)

    @on.message(F.text == "➡ Далі")
    async def next_pizza(self, message: Message, state: FSMContext) -> None:
        pizzas = get_pizzas()
        p_len = len(pizzas)
        data = await state.get_data()
        step = data["step"]
        if step == p_len - 1:
            await message.answer("Це остання піца")
            await self.wizard.retake(step=step)
        else:
            await self.wizard.retake(step=step + 1)

    @on.message(F.text == "⬅ Назад")
    async def previous_pizza(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        step = data["step"]
        previous_step = step - 1
        if previous_step < 0:
            await message.answer("Це перша піца")
            await self.wizard.retake(step=step)
        else:
            await self.wizard.retake(step=previous_step)

    @on.message(F.text == "🚫 Вихід")
    async def cancel(self, message: Message, state: FSMContext) -> Any:
        await state.clear()
        return await self.wizard.goto(CatalogSettings)

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class SendContact(Scene, state="send_contact"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        markup = ReplyKeyboardBuilder()
        markup.button(text="Надіслати контакт", request_contact=True)
        await message.answer(
            text="Надішліть свій контакт.",
            reply_markup=markup.as_markup(resize_keyboard=True)
        )

    @on.message(F.contact)
    async def contact(self, message: Message, state: FSMContext) -> Any:
        await message.answer(text="Відправляємо контакт...")
        await state.update_data(phone_num=message.contact.phone_number)
        await state.update_data(contact_name=message.contact.first_name)
        await state.update_data(contact_username=message.chat.username)
        await self.wizard.goto(SendLocation)

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class SendLocation(Scene, state="send_location"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        markup = ReplyKeyboardBuilder()
        markup.button(text="Надіслати свою геолокацію", request_location=True)
        await message.answer(
            text="Надішліть свою геолокацію. \nНа разі ця функція доступна лише в мобільній версії Телеграму",
            reply_markup=markup.as_markup(resize_keyboard=True)
        )

    @on.message(F.location)
    async def location(self, message: Message, state: FSMContext) -> Any:
        await state.update_data(latitude=message.location.latitude)
        await state.update_data(longitude=message.location.longitude)
        markup = ReplyKeyboardBuilder()
        markup.button(text="Готово")
        await message.answer(
            text='Натисніть кнопку "Готово".',
            reply_markup=markup.as_markup(resize_keyboard=True)
        )
        await state.set_state(SendData.sending)

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class Summary(Scene, state="summary"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        size = data["size"]
        price = data["pizza"]["price"]
        pizza_type = data["type"]
        number_of = data["numberOf"]
        if size > 26:
            price += 5 * (size - 26)
        total_price = price * int(number_of)
        markup = ReplyKeyboardBuilder()
        markup.button(text="✔ Готово")
        markup.button(text="❌ Скасувати")
        await state.update_data(total_price=total_price)
        await message.answer_photo(
            photo=FSInputFile(
                path=data["pizza"]["imageUrl"]
            ),
            caption=f'''{data["pizza"]["title"]}\n
            Ціна – {total_price} грн.\n
            Тип – {pizza_type}\n
            Розмір – {size} см.\n
            Кількість – {number_of} шт.''',
            reply_markup=markup.as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "✔ Готово")
    async def done(self, message: Message) -> Any:
        return await self.wizard.goto(SendContact)

    @on.message(F.text == "❌ Скасувати")
    async def cancel(self, message: Message, state: FSMContext) -> Any:
        await message.answer(text="❌ Замовлення скасовано")
        await state.clear()
        await message.answer(
            "Вітаємо вас в нашому боті для замовлення піци.",
            reply_markup=main,
        )
        await state.clear()
        await state.set_state(StartStatus.choose)

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class ChooseNumOf(Scene, state="choose_num_of"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        await message.answer(
            text="Введіть кількість обраної піци, яку ви хочете замовити.",
            reply_markup=ReplyKeyboardRemove()
        )

    @on.message(F.text)
    async def num_of(self, message: Message, state: FSMContext) -> Any:
        if message.text.isdigit() and message.text != "0":
            await state.update_data(numberOf=int(message.text))
            return await self.wizard.goto(Summary)
        else:
            await message.answer("Невірний формат вводу.")

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class ChooseSize(Scene, state="choose_size"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizza = data["pizza"]
        sizes_i = pizza["sizes"]
        markup = ReplyKeyboardBuilder()
        for i in sizes_i:
            markup.button(text=str(i))
        await message.answer(
            text="Виберіть розмір піци.\nЦіна збільшується на 5 грн. за кожен сантиметр на який розмір перевищує 26 см",
            reply_markup=markup.adjust(2).as_markup(resize_keyboard=True)
        )

    @on.message(F.text)
    async def size(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizza = data["pizza"]
        sizes_i = pizza["sizes"]
        for i in sizes_i:
            if message.text == str(i):
                await state.update_data(size=int(message.text))
                return await self.wizard.goto(ChooseNumOf)
        return await message.answer(text="Такої піци немає.")

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class ChooseType(Scene, state="choose_type"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizza = data["pizza"]
        types_i = pizza["types"]
        markup = ReplyKeyboardBuilder()
        for i in types_i:
            markup.button(text=types[i])
        await message.answer(
            text="Вибери тип піци",
            reply_markup=markup.as_markup(resize_keyboard=True)
        )

    @on.message(F.text)
    async def type(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        pizza = data["pizza"]
        types_i = pizza["types"]
        for i in types_i:
            if message.text == types[i]:
                await state.update_data(type=message.text)
                return await self.wizard.goto(ChooseSize)
        return await message.answer(text="Такої піци немає.")

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class CatalogScene(Scene, state="catalog"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:

        pizzas = get_pizzas()
        p_len = len(pizzas)

        pizza = pizzas[step]

        markup = ReplyKeyboardBuilder()
        markup.button(text="✔ Обрати")
        if not step == p_len - 1:
            markup.button(text="➡ Далі")
        if step > 0:
            markup.button(text="⬅ Назад")
        markup.button(text="🚫 Вихід")

        await state.update_data(step=step)
        await state.update_data(pizza=pizza)
        await message.reply_photo(
            photo=FSInputFile(
                path=pizza["imageUrl"]
            ),
            caption=f'{pizza["title"]}\nЦіна – {pizza["price"]} грн. за мінімальний розмір ',
            reply_markup=markup.adjust(1, 2, 1).as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "✔ Обрати")
    async def choose_pizza(self, message: Message) -> None:
        return await self.wizard.goto(ChooseType)

    @on.message(F.text == "➡ Далі")
    async def next_pizza(self, message: Message, state: FSMContext) -> None:
        pizzas = get_pizzas()
        p_len = len(pizzas)
        data = await state.get_data()
        step = data["step"]
        if step == p_len - 1:
            await message.answer("Це остання піца")
            await self.wizard.retake(step=step)
        else:
            await self.wizard.retake(step=step + 1)

    @on.message(F.text == "⬅ Назад")
    async def previous_pizza(self, message: Message, state: FSMContext) -> None:
        data = await state.get_data()
        step = data["step"]
        previous_step = step - 1
        if previous_step < 0:
            await message.answer("Це перша піца")
            await self.wizard.retake(step=step)
        else:
            await self.wizard.back(step=previous_step)

    @on.message(F.text == "🚫 Вихід")
    async def cancel(self, message: Message, state: FSMContext) -> Any:
        await message.answer(
            "Вітаємо вас в нашому боті для замовлення піци.",
            reply_markup=main,
        )
        await state.clear()
        await state.set_state(StartStatus.choose)

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


class AddPizzaDone(Scene, state="add_pizza_done"):
    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext) -> Any:
        data = await state.get_data()
        if "title" not in data:
            await message.answer("Ви ще не додали назву піци.")
            return await self.wizard.goto(AddPizza)
        elif "types" not in data:
            await message.answer("Ви ще не додали тип піци.")
            return await self.wizard.goto(AddPizza)
        elif "price" not in data:
            await message.answer("Ви ще не додали ціну піци.")
            return await self.wizard.goto(AddPizza)
        elif "image" not in data:
            await message.answer("Ви ще не додали картинку для піци.")
            return await self.wizard.goto(AddPizza)
        else:
            if "sizes" not in data:
                data.update(sizes=[26])
            image = data["image"]
            image_name = data["image_name"]
            file_name = f"./static/Img/{image_name}"
            await bot.download(image, destination=file_name)
            data.update(imageUrl=file_name)
            insert_object(data)
            await state.clear()
            pizzas = get_pizzas()
            await self.wizard.set_data({"pizzas": pizzas})
            await message.answer("Піцу додано")
            return await self.wizard.goto(CatalogSettings)


class AddPizzaPhoto(Scene, state="add_pizza_photo"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        await message.answer("Надішліть картинку піци\n(У вигляді файлу. Це важливо!)")

    @on.message(F.document)
    async def upload_file(self, message: Message, state: FSMContext) -> Any:
        if file_exists(message.document.file_name):
            await message.answer("Файл з такою назвою вже присутній в базі даних.")
        else:
            await state.update_data(image=message.document)
            await state.update_data(image_name=message.document.file_name)
            await message.answer("Картинку додано.")
            return await self.wizard.goto(AddPizza)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class AddPizzaPrice(Scene, state="add_pizza_price"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        await message.answer("Введіть ціну", reply_markup=ReplyKeyboardRemove())

    @on.message(F.text)
    async def new_price(self, message: Message, state: FSMContext) -> Any:
        if message.text.isdigit():
            await state.update_data(price=int(message.text))
            await message.answer("Ціну додано")
            return await self.wizard.goto(AddPizza)
        else:
            await message.answer("Ціна повинна бути цілим числом")

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class AddPizzaSize(Scene, state="add_pizza_size"):
    sizes = []

    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        sizes = AddPizzaSize.sizes
        sizes.clear()
        sizes.append(26)
        markup = ReplyKeyboardBuilder()
        markup.button(text="Готово")
        await message.answer(
            "Введіть розмір піци (не менше 27см.)",
            reply_markup=markup.as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "Готово")
    async def done(self, message: Message, state: FSMContext) -> Any:
        sizes = AddPizzaSize.sizes
        sizes.sort()
        await state.update_data(sizes=sizes)
        return await self.wizard.goto(AddPizza)

    @on.message(F.text)
    async def new_size(self, message: Message) -> Any:
        sizes = AddPizzaSize.sizes
        if len(sizes) != 4:
            if message.text.isdigit():
                if int(message.text) in sizes:
                    await message.answer("Цей розмір вже є")
                else:
                    if int(message.text) >= 27:
                        sizes.append(int(message.text))
                        await message.answer(
                            f"Розмір додано.\nВи можете додати ще {4 - len(sizes)}, або завершити "
                            f"додавання\nнатиснувши кнопку 'Готово'"
                        )
                    else:
                        await message.answer("Розмір повинен бути не менше 27см.")
            else:
                await message.answer("Розмір має бути цілим числом")
        else:
            await message.answer("Ви не можете додати більше розмірів")

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class AddPizzaType(Scene, state="add_pizza_type"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        markup = ReplyKeyboardBuilder()
        markup.button(text="Тонка")
        markup.button(text="Традиційна")
        markup.button(text="Тонка і традиційна")
        await message.answer(
            "Виберіть тип піци",
            reply_markup=markup.as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "Тонка")
    async def thin_type(self, message: Message, state: FSMContext) -> Any:
        await state.update_data(types=[0])
        await message.answer("Тип додано.")
        return await self.wizard.goto(AddPizza)

    @on.message(F.text == "Традиційна")
    async def traditional_type(self, message: Message, state: FSMContext) -> Any:
        await state.update_data(types=[1])
        await message.answer("Тип додано.")
        return await self.wizard.goto(AddPizza)

    @on.message(F.text == "Тонка і традиційна")
    async def both_types(self, message: Message, state: FSMContext) -> Any:
        await state.update_data(types=[0, 1])
        await message.answer("Тип додано.")
        return await self.wizard.goto(AddPizza)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class AddPizzaTitle(Scene, state="add_pizza_title"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        await message.answer("Введіть назву піци.")

    @on.message(F.text)
    async def add_pizza_title(self, message: Message, state: FSMContext) -> Any:
        await state.update_data(title=message.text)
        await message.answer("Назву додано.")
        return await self.wizard.goto(AddPizza)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда.")


class AddPizza(Scene, state="add_pizza"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        await message.answer(text="Виберіть дію", reply_markup=add_pizza)

    @on.message(F.text == "Додати назву")
    async def add_title(self, message: Message) -> Any:
        return await self.wizard.goto(AddPizzaTitle)

    @on.message(F.text == "Додати тип")
    async def add_type(self, message: Message) -> Any:
        return await self.wizard.goto(AddPizzaType)

    @on.message(F.text == "Додати розмір")
    async def add_size(self, message: Message) -> Any:
        return await self.wizard.goto(AddPizzaSize)

    @on.message(F.text == "Додати ціну")
    async def add_price(self, message: Message) -> Any:
        return await self.wizard.goto(AddPizzaPrice)

    @on.message(F.text == "Додати картинку")
    async def add_picture(self, message: Message) -> Any:
        return await self.wizard.goto(AddPizzaPhoto)

    @on.message(F.text == "✔ Готово")
    async def done(self, message: Message) -> Any:
        return await self.wizard.goto(AddPizzaDone)

    @on.message(F.text == "❌ Скасувати")
    async def cancel(self, message: Message, state: FSMContext) -> Any:
        await state.clear()
        await message.answer("Операцію скасовано.")
        return await self.wizard.goto(CatalogSettings)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда")


class CatalogSettings(Scene, state="catalog_settings"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:
        markup = ReplyKeyboardBuilder()
        markup.button(text="Додати піцу")
        markup.button(text="Змінити дані піци")
        markup.button(text="🚫 Вихід")
        await message.answer(
            "Виберіть опцію",
            reply_markup=markup.adjust(2, 1).as_markup(resize_keyboard=True)
        )

    @on.message(F.text == "🚫 Вихід")
    async def cancel(self, message: Message, state: FSMContext) -> Any:
        await message.answer(
            "Вітаємо вас в нашому боті для замовлення піци.",
            reply_markup=main,
        )
        await state.set_state(StartStatus.choose)
        await self.wizard.leave()

    @on.message(F.text == "Додати піцу")
    async def add_pizza(self, message: Message) -> Any:
        await self.wizard.goto(AddPizza)

    @on.message(F.text == "Змінити дані піци")
    async def change_pizza(self, message: Message) -> Any:
        await self.wizard.goto(ChangePizza)

    @on.message(F)
    async def unknown_command(self, message: Message) -> Any:
        await message.answer("Невідома команда")


class CheckCode(Scene, state="check_code"):
    @on.message.enter()
    async def on_enter(self, message: Message) -> Any:

        await message.answer(
            text="Введіть код",
            reply_markup=ReplyKeyboardRemove()
        )

    @on.message(F.text)
    async def check_code(self, message: Message, state: FSMContext) -> Any:
        if message.text == CODE:
            await self.wizard.goto(CatalogSettings)
            await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        else:
            await message.answer(text="Невірний код")
            await message.answer(
                "Вітаємо вас в нашому боті для замовлення піци.",
                reply_markup=main,
            )
            await state.set_state(StartStatus.choose)

    @on.message(F)
    async def unknown_command(self, message: Message) -> None:
        await message.answer("Невідома команда")


router = Router(name=__name__)

user_data = {}

router.message.register(CatalogScene.as_handler(), F.text == "Переглянути каталог", StartStatus.choose)
router.message.register(CheckCode.as_handler(), F.text == "Змінити каталог", StartStatus.choose)


@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer(
        "Вітаємо вас в нашому боті для замовлення піци.",
        reply_markup=main,
    )

    await state.set_state(StartStatus.choose)


@router.message(F.text == "Готово", SendData.sending)
async def sending(message: Message, state: FSMContext):
    data = await state.get_data()
    await bot.send_contact(chat_id=CHANNEL_FOR_RECEIVING_ORDERS, phone_number=data["phone_num"], first_name=data["contact_name"])
    markup = InlineKeyboardBuilder()
    markup.button(
        text="Перейти до контакту",
        url=f"https://t.me/{data['contact_username']}"
    )
    await bot.send_location(chat_id=CHANNEL_FOR_RECEIVING_ORDERS, latitude=data["latitude"], longitude=data["longitude"],
                            reply_markup=markup.as_markup())

    await bot.send_photo(
        chat_id=CHANNEL_FOR_RECEIVING_ORDERS,
        photo=FSInputFile(
            path=data["pizza"]["imageUrl"]
        ),
        caption=f'''{data["pizza"]["title"]}\n
            Ціна – {data["total_price"]} грн.\n
            Тип – {data["type"]}\n
            Розмір – {data["size"]} см.\n
            Кількість – {data["numberOf"]} шт.\n
            Замовник – <a href="https://t.me/{data["contact_username"]}">{data["contact_name"]}</a>''',
        parse_mode="HTML",
    )

    await message.answer(text="Замовлення відправлено!")
    await state.clear()
    await message.answer(
        "Вітаємо вас в нашому боті для замовлення піци.",
        reply_markup=main,
    )
    await state.set_state(StartStatus.choose)


@router.message(F, StartStatus.choose)
async def unknown(message: Message):
    await message.answer("Не розумію.")
