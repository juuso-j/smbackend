from modeltranslation.translator import TranslationOptions, translator


from data_view.models import (
    UnitGroup,
    Unit,
)


class UnitGroupTranslationOptions(TranslationOptions):
    fields = ("name", "description")

translator.register(UnitGroup, UnitGroupTranslationOptions)


class UnitTranslationOptions(TranslationOptions):
    fields = ("name","address")
translator.register(Unit, UnitTranslationOptions)