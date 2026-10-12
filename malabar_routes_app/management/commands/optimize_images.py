from django.apps import apps
from django.core.management.base import BaseCommand

from ...models import OptimizedImageModel
from ...utils.image_optimizer import convert_to_webp, generate_variants


class Command(BaseCommand):
    help = "Convert existing images to WebP and generate size variants."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List what would be converted without changing or deleting anything.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        done = skipped = failed = 0

        for model in apps.get_models():
            if not issubclass(model, OptimizedImageModel) or model._meta.abstract:
                continue

            for obj in model.objects.all():
                for field in model.image_fields:
                    f = getattr(obj, field, None)
                    if not f or not f.name or not f.storage.exists(f.name):
                        skipped += 1
                        continue

                    try:
                        old_name = f.name

                        if dry_run:
                            action = (
                                "variants only"
                                if old_name.lower().endswith(".webp")
                                else "convert to webp + variants"
                            )
                            self.stdout.write(
                                f"[dry-run] {model.__name__} #{obj.pk} {field}: {old_name} -> {action}"
                            )
                            done += 1
                            continue

                        if not old_name.lower().endswith(".webp"):
                            with f.storage.open(old_name) as src:
                                webp = convert_to_webp(src, old_name)
                            f.save(webp.name, webp, save=False)
                            obj.save(update_fields=[field])
                            f.storage.delete(old_name)

                        generate_variants(getattr(obj, field))
                        done += 1
                    except Exception as e:
                        failed += 1
                        self.stderr.write(f"{model.__name__} #{obj.pk} {field}: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Done: {done}, skipped: {skipped}, failed: {failed}"
        ))