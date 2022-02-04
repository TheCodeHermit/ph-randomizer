from PIL import Image
import click
from ndspy import graphics2D, lz10, narc, rom


class AutoList(list):
    def __setitem__(self, index, value):
        if index >= len(self):
            self.extend([None] * (index + 1 - len(self)))
        list.__setitem__(self, index, value)


def extract_image(image: bytes, palette: list) -> Image:
    img = Image.new("RGB", (256, 128), (0, 0, 0))
    for y in range(128):
        for x in range(256):
            px = palette[image[y * 256 + x]]
            img.putpixel((x, y), px)
    return img


def insert_image(img: Image, palette: list):
    image = AutoList()
    for y in range(128):
        for x in range(256):
            px = img.getpixel((x, y))
            image[y * 256 + x] = palette.index(px)
    return bytes(image)


@click.command()
@click.option(
    "-i/-e",
    "--insert/--extract",
    default=False,
    help="Whether to insert a new title screen image, or extract the existing one",
)
@click.option("--input", type=str, required=True, help="Source ROM")
@click.option(
    "--output",
    type=str,
    required=True,
    help="File to save output to (either a new ROM or an image)",
)
@click.option(
    "--image", type=str, required=False, help="(insert only) Image to replace title screen with"
)
def title_screen(insert: bool, input: str, output: str, image: str):
    nds_rom = rom.NintendoDSRom.fromFile(input)
    narc_file = narc.NARC(lz10.decompress(nds_rom.getFileByName("English/Menu/Tex2D/title.bin")))
    colors = graphics2D.loadPalette(narc_file.getFileByName("title.ntfp"))

    if insert:
        bmp = Image.open(image).convert("RGB")
        new_image = insert_image(
            bmp,
            [
                (r, g, b)
                for (r, g, b, _) in graphics2D.loadPalette(narc_file.getFileByName("title.ntfp"))
            ],
        )
        narc_file.setFileByName("title.ntft", new_image)
        nds_rom.setFileByName("English/Menu/Tex2D/title.bin", lz10.compress(narc_file.save()))
        nds_rom.saveToFile(output)

    else:
        image = narc_file.getFileByName("title.ntft")
        bmp: Image = extract_image(image, colors)
        if not output.endswith(".bmp"):
            output = f"{output}.bmp"
        bmp.save(output, compress_level=0)


if __name__ == "__main__":
    title_screen()
