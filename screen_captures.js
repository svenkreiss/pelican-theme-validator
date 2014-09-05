var fs = require('fs');
var webpage = require('webpage');
var pageWidth = 1024,
    pageHeight = 768;

var themes = fs.list('output_all');
console.log(themes);
var count = 0;

themes.map(function(t) {
    // filter invisibles
    if (t[0] == '.') return;
    // only look at directories
    if (!fs.isDirectory('output_all/'+t)) return;

    console.log(t);

    // take screenshot
    count += 1;
    var page = webpage.create();
    page.viewportSize = { width: pageWidth, height: pageHeight };
    page.clipRect = { top: 0, left: 0, width: pageWidth, height: pageHeight };
    page.open('file://'+fs.absolute('output_all/'+t+'/output/index.html'), function() {
        console.log('rendering');
        page.render('output_all/'+t+'/screen_capture.png');
        count -= 1;
    });
});

function wait() {
    if (count==0) {
        phantom.exit();
    }
    setTimeout(wait, 500);
    console.log(count);
}
setTimeout(wait, 500);

