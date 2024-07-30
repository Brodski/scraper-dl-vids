const sharp = require('sharp');

// const ExifReader = require('exifreader');
// const ExifReader = require('exif-reader');
// const exifErrors = ExifReader.errors;



class Transform {
    
    static async reduceImg({image, filename, value}) {
        console.log("Got reduce value of: ", value);
        console.log("got image:", image)
        const imageSharp = sharp(image);
        const meta = await imageSharp.metadata();
        const format = meta.format;

        // percent
        if (value > 0 && value < 1) {
            value = Math.round(meta.width * value);
        }
        const imgNewBuffer = await imageSharp.resize(value).toBuffer();

        const imgNew = sharp(imgNewBuffer);
        const metaNew = await imgNew.metadata();
        const isSave = false;
        
        let filename_new = `${filename}_${metaNew.width}x${metaNew.height}.${format}`

        let img = null;
        if (isSave) {
            img = await imgNew.toFile(`./imgs/${filename_new}`);
        } 
        else {
            img = await imgNew.toBuffer();
        }
        return {img, format, filename_new};
    }
    
    // static async reduceByPercent({image, filename, percent}) {
    //     return this._reduceImgAux({image, filename, "value": percent});
    // }
    
    // static async reduceToPixels({image, filename, width}) {
    //     return this._reduceImgAux({image, filename, "value": width});
    // }
    
    static async halfItWithmeta({image, filename, width, height, percent}) {
        const imageSharp = sharp(image);
        // const image = sharp('imgs/thumb.jpg');

        let meta = await imageSharp.metadata()
        const format = meta.format
        console.log("META!")
        console.log(meta)
        console.log(aspectRatio)
        console.log(format)
        // filename = filename + w

        let imgNewBuffer = await imageSharp.resize(width).toBuffer()
        let imgNew = sharp(imgNewBuffer);
        let metaNew = await imgNew.metadata()
        console.log("-------------------")
        
        console.log("imgNew:",imgNew)
        console.log("aspect:", metaNew.width / metaNew.height)
        console.log("metaNew", metaNew)
        console.log("metaNew.width", metaNew.width)
        console.log("metaNew.height", metaNew.height)
        // console.log(sharpNew)
        // imageSharp.resize(Math.round(meta.width / 2))
        await imgNew.toFile(`./imgs/${filename}${metaNew.width}${metaNew.height}.${format}`)
    }
}

module.exports = Transform;