import json

from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

from openslides.utils.access_permissions import required_user
from openslides.utils.cache import ElementCache, element_cache as _element_cache
from openslides.utils.cache_providers import MemoryCacheProvider
from openslides.utils.projector import get_projector_data
from openslides.utils.utils import (
    get_element_id,
    get_model_from_collection_string,
    split_element_id,
)


class FakeElementCache(ElementCache):
    def __init__(self, *args, **kwargs):
        self._extra = {}
        super().__init__(*args, **kwargs)

    def add_extra(self, element_id, data):
        self._extra[element_id.encode()] = json.dumps(data).encode()

    def clear_extras(self):
        self._extra = {}

    async def get_all_data_list(self, user_id=None):
        all_data = await self.cache_provider.get_all_data()
        for k, v in self._extra.items():
            all_data[k] = v
        return await self.format_all_data(all_data, user_id)

    async def get_collection_data(self, collection):
        data = await super().get_collection_data(collection)
        for k, v in self._extra.items():
            c, id = split_element_id(k)
            if c == collection and id in data:
                data[id] = json.loads(v.decode())
        return data

    async def get_element_data(self, collection, id, user_id=None):
        element_id = get_element_id(collection, id)
        if element_id.encode() in self._extra:
            encoded_element = self._extra[element_id.encode()]
        else:
            encoded_element = await self.cache_provider.get_element_data(element_id)

        if encoded_element is None:
            return None
        element = json.loads(encoded_element.decode())  # type: ignore
        element.pop(
            "_no_delete_on_restriction", False
        )  # remove special field for get_data_since

        if user_id is not None:
            element = await self.restrict_element_data(element, collection, user_id)
        return element


element_cache = FakeElementCache(cache_provider_class=MemoryCacheProvider)


class FakeAllDataProvider:
    async def get(self, collection, id):
        return await element_cache.get_element_data(collection, id)

    async def get_collection(self, collection):
        return await element_cache.get_collection_data(collection)

    async def exists(self, collection, id):
        model = await self.get(collection, id)
        return model is not None


class Command(BaseCommand):
    help = "Exports test data to OS3+"

    def handle(self, *args, **options):
        async_to_sync(self.handle_async)()

    async def handle_async(self):
        await _element_cache.async_ensure_schema_version()
        await element_cache.async_ensure_schema_version()
        self.all_data = await element_cache.get_all_data_list()

        restricted = {}
        for user_id in self.get_user_ids():
            restricted[user_id] = await self.restrict(user_id)

        required_users = await self.get_required_users()
        projector = await self.get_projector_data()

        export = {
            "all_data": self.all_data,
            "restricted_data": restricted,
            "required_users": required_users,
            "projectors": projector,
        }
        json.dump(export, open("export.json", "w"), indent=2)

    def get_user_ids(self):
        return [user["id"] for user in self.all_data["users/user"]]

    async def restrict(self, user_id):
        return await element_cache.get_all_data_list(user_id)

    async def get_required_users(self):
        required = {}  # map element_id <-> List<user_id>
        for collection, elements in self.all_data.items():
            get_user_ids = required_user.callables.get(collection)
            if not get_user_ids:
                continue

            can_see_perm = get_model_from_collection_string(
                collection
            ).can_see_permission
            for element in elements:
                element_id = get_element_id(collection, element["id"])
                ids = list(await get_user_ids(element))
                required[element_id] = {"ids": ids, "perm": can_see_perm}
        return required

    async def get_projector_data(self):
        projector1 = None
        for projector in self.all_data["core/projector"]:
            if projector["id"] == 1:
                projector1 = projector

        if projector1 is None:
            raise RuntimeError()
        projector1 = json.loads(json.dumps(projector1))

        overwrites = self.get_projector_overwrites()
        return [await self.get_projection(overwrite) for overwrite in overwrites]

    async def get_projection(self, overwrite):
        for element_id, model in overwrite.items():
            element_cache.add_extra(element_id, model)

        data = {
            "overwrite": overwrite,
            "data": (await get_projector_data(None, FakeAllDataProvider()))[1][0],  # type: ignore
        }

        element_cache.clear_extras()
        return data

    def get_projector_overwrites(self):
        projector1 = self.build_fake_projector(1, 2)
        projector2 = self.build_fake_projector(2, 2)

        overwrites = [
            # Invalid ones
            {"core/projector:1": self.set_element(projector1, {})},
            {"core/projector:1": self.set_element(projector1, {"name": "unknown"})},
            {"core/projector:2": self.set_element(projector1, {"name": [], "id": 2})},
            # valid elements
            {
                "core/projector:1": self.set_element(
                    projector1, {"name": "agenda/item-list", "only_main_items": False}
                )
            },
            {
                "core/projector:1": self.set_element(
                    projector1, {"name": "agenda/item-list", "only_main_items": True}
                )
            },
            {
                "core/projector:1": self.set_element(
                    projector1, {"name": "core/clock", "stable": True}
                )
            },
        ]

        for collection in (
            "motions/motion-block",
            "users/user",
            "core/countdown",
            "core/projector-message",
            "assignments/assignment",
            "motions/motion",
            "motions/motion-poll",
            "assignments/assignment-poll",
            "mediafiles/mediafile",
            "topics/topic",
            "agenda/list-of-speakers",
        ):
            for model in self.all_data[collection]:
                element = {"name": collection, "id": model["id"]}
                overwrites.append(
                    {"core/projector:1": self.set_element(projector1, element)}
                )
                for e in self.get_invalid_elements(collection):
                    overwrites.append(
                        {"core/projector:1": self.set_element(projector1, e)}
                    )
                for e in self.get_clos_elements():
                    overwrites.append(
                        {
                            "core/projector:1": self.set_element(projector1, e),
                            "core/projector:2": self.set_element(projector2, element),
                        }
                    )

        self.add_extra_motion_overwrites(overwrites, projector1)
        return overwrites

    def add_extra_motion_overwrites(self, overwrites, projector1):
        motion_configs = (
            "motions_disable_sidebox_on_projector",
            "motions_hide_referring_motions",
            "motions_disable_text_on_projector",
            "motions_disable_reason_on_projector",
            "motions_disable_recommendation_on_projector",
        )
        for model in self.all_data["motions/motion"]:
            element = {"name": "motions/motion", "id": model["id"], "mode": "final"}
            overwrites.append(
                {"core/projector:1": self.set_element(projector1, element)}
            )

            for config_value in (True, False):
                overwrite = {
                    "core/projector:1": self.set_element(
                        projector1, {"name": "motions/motion", "id": model["id"]}
                    ),
                }
                for config_key in motion_configs:
                    config = self.build_fake_config(config_key, config_value)
                    overwrite[f"core/config:{config['id']}"] = config
                overwrites.append(overwrite)

    def build_fake_config(self, key, value):
        id = None
        for config in self.all_data["core/config"]:
            if config["key"] == key:
                id = config["id"]

        if id is None:
            raise RuntimeError()

        return {"id": id, "key": key, "value": value}

    def get_invalid_elements(self, collection):
        return [
            {"name": collection},
            {"name": collection, "id": "a string"},
            {"name": collection, "id": 1337},
        ]

    def get_clos_elements(self):
        return [
            {"name": "agenda/current-list-of-speakers", "stable": False},
            {"name": "agenda/current-speaker-chyron", "stable": True},
            {"name": "agenda/current-list-of-speakers-overlay", "stable": True},
        ]

    def build_fake_projector(self, id, reference_id):
        return {
            "id": id,
            "elements": [{"name": "mediafiles/mediafile", "id": 3}],
            "elements_preview": [],
            "elements_history": [[{"name": "assignments/assignment", "id": 1}]],
            "scale": 0,
            "scroll": 0,
            "name": "Default projector",
            "width": 1200,
            "aspect_ratio_numerator": 16,
            "aspect_ratio_denominator": 9,
            "reference_projector_id": reference_id,
            "projectiondefaults_id": [],
            "color": "#000000",
            "background_color": "#ffffff",
            "header_background_color": "#317796",
            "header_font_color": "#f5f5f5",
            "header_h1_color": "#317796",
            "chyron_background_color": "#317796",
            "chyron_font_color": "#ffffff",
            "show_header_footer": True,
            "show_title": True,
            "show_logo": True,
        }

    def set_element(self, projector, element):
        projector = json.loads(json.dumps(projector))
        projector["elements"] = [element]
        return projector
