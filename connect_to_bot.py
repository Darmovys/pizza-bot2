import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.scene import SceneRegistry
from handlers.instructions import (router, CatalogScene, ChooseType, ChooseSize, ChooseNumOf, Summary, SendLocation,
                                   SendContact, CatalogSettings, CheckCode, AddPizza, AddPizzaTitle, AddPizzaType,
                                   AddPizzaSize, AddPizzaPrice, AddPizzaPhoto, AddPizzaDone, ChangePizza,
                                   ChangePizzaSelected, ChangePizzaTitle, ChangePizzaTypes, ChangePizzaSizes,
                                   DeletePizzaSize, AddNewPizzaSize, CheckPizzaSize, UpdatePizzaSize, ChangePizzaPrice,
                                   ChangePizzaPhoto)


TOKEN = "Insert your token API"

bot = Bot(TOKEN)


def create_dispatcher():
    dp = Dispatcher(
        events_isolation=SimpleEventIsolation(),
    )
    dp.include_router(router)
    scene_registry = SceneRegistry(dp)
    scene_registry.add(CatalogScene, ChooseType, ChooseSize, ChooseNumOf, Summary, SendLocation, SendContact,
                       CatalogSettings, CheckCode, AddPizza, AddPizzaTitle, AddPizzaType, AddPizzaSize, AddPizzaPrice,
                       AddPizzaPhoto, AddPizzaDone, ChangePizza, ChangePizzaTitle, ChangePizzaSelected,
                       ChangePizzaTypes, ChangePizzaSizes, DeletePizzaSize, AddNewPizzaSize, CheckPizzaSize,
                       UpdatePizzaSize, ChangePizzaPrice, ChangePizzaPhoto)
    return dp


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = create_dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
