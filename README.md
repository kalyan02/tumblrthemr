## Tumblr Themr

TumblrThemr is a standalone tool to develop tumblr themes offline on your mac! It lets you get rid of the painful process of copy pasting your theme onto tumblr's interface to preview it and lets you use your favorite editor for development.

Themes are rendered against the default tumblr data. You can also test against your own tumble blog, for that you will need to import your tumble blog's data , from Tumblr Themr itself, using your Tumblr developer API Key.

### Download

[http://tumblrthemr.com/TumblrThemr.zip](http://tumblrthemr.com/TumblrThemr.zip)

### Getting started

To run the app, follow these steps:

 * Run TumblrThemr.app  
![Web Interface](https://raw.github.com/kalyan02/tumblrtemplatr/master/etc/screenshot_2.png)

 * Select the directory containing your themes  

```
Example directory structure  
/projects                 <-- *you need to pick this*
  +--theme_in_development
  |  +-index.html         <-- index.html must be your theme
  |  +-style.css
  |
  +--theme2
```

 * Optionally select the port (default:13323)
 * Click on 'Start Server' to start the offline tumblr server
 * A browser window with the default webpage will open  
![Web Interface](https://raw.github.com/kalyan02/tumblrtemplatr/master/etc/screenshot_1.png)

### Preview your theme
 * From the homepage (default [http://localhost:13323](http://localhost:13323)) , you can select an available theme
 * If your theme doesn't appear, then you will have to stop the server and pick again
 * Open your theme from the "Select Project" section

### Testing your theme
Its simple - just refresh your browser after an edit and you can preview the changes - just as you would develop your html/css templates!

### Custom tumblr data

 * To test against your own tumblr blog/data, you will first need an API Key
 * If you do not have an API key, you will need to request for it here by registering a dummy application - [http://www.tumblr.com/oauth/apps](http://www.tumblr.com/oauth/apps)
 * In the "Import Data Source" section add your API Key and the tumblr blog's username
 * Select Import 
 
 
### Switching data source
 TumblrThemr allows you to test your themes against multiple data sources. If you want to switch data source, select the prefered source from "Select Data Source" section.

## Pre-requisits 
The .app file is a standalone bundle and does not have any dependencies

To build the app from source you will require the following 
 * python2.7
 * bottle
 * jinja2
 * wx [framework]
 * distutils

## Todo
 * Implement full tumblr spec
 * Add support for windows / py2exe

## Contribution
The full tumblr spec hasn't been implemented yet. If you would like to contribute,
please send a pull request and add your name to this section along with your commit.

* [kalyan02](http://twitter.com/kalyan02)

## License
This free software is released under [MIT License](http://opensource.org/licenses/MIT)
```
Copyright (c) 2013 Kalyan Chakravarthy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
