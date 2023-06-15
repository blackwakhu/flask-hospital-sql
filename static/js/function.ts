var imgs: string[] =  ["pexels-photo-1692693.jpeg", "photo-1504813184591-01572f98c85f.avif", "photo-1505751172876-fa1923c5c528.avif", 
"photo-1512678080530-7760d81faba6.avif", "photo-1519494026892-80bbd2d6fd0d.avif", "photo-1530026405186-ed1f139313f8.avif", 
"photo-1538108149393-fbbd81895907.avif", "photo-1551076805-e1869033e561.avif", "photo-1579684385127-1ef15d508118.avif", 
"photo-1584820927498-cfe5211fd8bf.avif", "premium_photo-1658506854326-52eab70cb236.avif", "premium_photo-1663013523060-7c833fe956ec.avif", 
"premium_photo-1663013549676-1eba5ea1d16e.avif", "woman in bed.jpg"]

function randomImage(imgs: string[]): string {
    return imgs[Math.floor(Math.random() * imgs.length)];
}

setInterval(function() {
    var body: any = document.querySelector("body");
    body.style.backgroundImage = 'url(/static/hospital/'+randomImage(imgs)+')'
}, 2500)