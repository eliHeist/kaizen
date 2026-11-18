"""Abstract model building blocks shared by every content app."""
import logging

from django.db import models
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# Uploaded photos straight off a camera are often 6000px+ and several MB.
# Anything larger than this is downscaled in place after upload.
MAX_IMAGE_PX = 2400


def unique_slug(instance, value, slug_field='slug', max_length=None):
    """Slugify ``value`` and append -2, -3... until it's unique for the model."""
    field = instance._meta.get_field(slug_field)
    max_length = max_length or field.max_length
    base = (slugify(value) or 'item')[:max_length]
    candidate, n = base, 2
    qs = type(instance)._default_manager.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(**{slug_field: candidate}).exists():
        suffix = f'-{n}'
        candidate = f'{base[:max_length - len(suffix)]}{suffix}'
        n += 1
    return candidate


def downscale_image(fieldfile, max_px=MAX_IMAGE_PX):
    """Shrink a stored image in place if either side exceeds ``max_px``."""
    if not fieldfile:
        return
    try:
        from PIL import Image, ImageOps

        path = fieldfile.path
        with Image.open(path) as img:
            if max(img.size) <= max_px:
                return
            fmt = img.format
            img = ImageOps.exif_transpose(img)
            img.thumbnail((max_px, max_px), Image.LANCZOS)
            if fmt == 'JPEG' and img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            img.save(path, format=fmt, quality=82, optimize=True)
    except (NotImplementedError, ValueError, OSError):
        # Remote storage (no .path) or an unreadable file: leave it alone.
        logger.warning('Could not downscale %s', fieldfile, exc_info=True)


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Slugged(models.Model):
    """Adds a unique slug filled from ``slug_source`` when left blank."""
    slug = models.SlugField(
        max_length=140, unique=True, blank=True,
        help_text='Used in the page URL. Leave blank to generate it from the name.',
    )
    slug_source = 'name'

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, getattr(self, self.slug_source))
        super().save(*args, **kwargs)


class SeoFields(models.Model):
    meta_title = models.CharField(
        'SEO title', max_length=70, blank=True,
        help_text='Optional. Title shown in Google results (about 60 characters). Defaults to the name.',
    )
    meta_description = models.CharField(
        'SEO description', max_length=160, blank=True,
        help_text='Optional. Snippet shown in Google results (about 155 characters). Defaults to the summary.',
    )

    class Meta:
        abstract = True


class OptimisedImages(models.Model):
    """Downscales newly uploaded files in the fields named in ``image_fields``."""
    image_fields = ()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        fresh = [
            name for name in self.image_fields
            if getattr(self, name) and not getattr(getattr(self, name), '_committed', True)
        ]
        super().save(*args, **kwargs)
        for name in fresh:
            downscale_image(getattr(self, name))


class Page(TimeStamped, Slugged, SeoFields, OptimisedImages):
    """A publicly addressable piece of content."""
    is_published = models.BooleanField(default=True, help_text='Untick to hide it from the site.')

    class Meta:
        abstract = True
