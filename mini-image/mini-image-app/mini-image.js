const sharp = require('sharp');

main()

async function main() {
    await textStuff()
    await textStuffCombo();
    await noisey();
    await logMetadata();
    await halfItWithmeta()
}

async function textStuffCombo() {
    const watermark = await sharp("./imgs/beard2deep.png")
    .resize(100) 
    .toBuffer();

  const result = await sharp("./imgs/thumb.jpg")
    .composite([{
      input: watermark, 
      blend: 'over', // places the image on top
      top: 10,
      left: 10 
    }])
    .toFile("./imgs/beardWatermark.jpg");
    
}

async function textStuff() {
    console.log("Text 0")
    await sharp({
        text: {
            text: 'Hello, world!',
            width: 400,
            height: 300 
        }
    }).toFile('./imgs/text_bw.png');
}

function logMetadata() {
    const imageSharp = sharp('imgs/thumb.jpg');
    imageSharp.metadata()
      .then(metadata => {
        const width = metadata.width;
        const height = metadata.height;
        const aspectRatio = width / height;
        console.log(`Aspect Ratio: ${aspectRatio}`);
        console.log('metadata')
        console.log(metadata)
      })
}

async function noisey() {
    // Generate RGB Gaussian noise
    await sharp({
        create: {
            width: 300,
            height: 200,
            channels: 3,
            noise: {
                type: 'gaussian',
                mean: 128,
                sigma: 30
            }
        }
    }).toFile('./imgs/noise.png');
}

async function halfItWithmeta() {
    const imageSharp = sharp('imgs/thumb.jpg');
    let meta = await imageSharp.metadata()
    console.log("META!")
    console.log(meta)
    imageSharp.resize(Math.round(meta.width / 2))
        .toFile('./imgs/halfsize.png')
}

function resizeWidth() {
    const imageSharp = sharp('imgs/thumb.jpg');
    imageSharp
      .resize(200) 
        //   .resize(200, 300)  //  width and height 
      .toFile('imgs/thumb200x300.jpg', (err, info) => { 
        if (err) throw err;
        console.log(info);
      });
}
