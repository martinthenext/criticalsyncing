##Backend##
###Resources###

* /sources 

*  *  method: GET

*  *  content-type: application/json

*  *  code: 200
  
            +pc ~: user$ curl -X GET http://127.0.0.1:8080/sources
            {"2": {"url": "http://bbc.com", "name": "bbc", "source_id": "2"}}

* /sources/\<id\>
 
*  *  method: GET
  
*  *  content-type: application/json
  
*  *  code: 200, 404

            +pc ~: user$ curl -X GET http://127.0.0.1:8080/sources
            {"2": {"url": "http://bbc.com", "name": "bbc", "source_id": "2"}}
            
* /sources/\<id\>

*  *  method: PUT

*  *  content-type: application/json

*  *  code: 200, 201, 406, 415

            +pc ~: user$ curl -X PUT -H "Content-Type: application/json" -d '{"url": "http://edition.cnn.com", "name": "cnn", "source_id": "1"}' http://127.0.0.1:8080/sources/1
            +pc ~: user$ curl -X GET http://127.0.0.1:8080/sources
            {{"1": {"url": "http://edition.cnn.com", "source_id": "1", "name": "cnn"}, "2": {"url": "http://bbc.com", "source_id": "2", "name": "bbc"}}
            
* /sources/\<id\>

*  *  method: DELETE

*  *  content-type: application/json

*  *  code: 200, 404

            +pc ~: user$ curl -X DELETE http://127.0.0.1:8080/sources/1
            +pc ~: user$ curl -X GET http://127.0.0.1:8080/sources
            {"2": {"url": "http://bbc.com", "name": "bbc", "source_id": "2"}}
            
###Commands

* /commands/crawl

*  * method: GET

*  * content-type: application/json

*  * code: 200, 202

            +pc ~: user$ curl -X GET http://127.0.0.1:8080/commands/crawl
            {"http://www.bbc.co.uk/news/technology-20465982": "2"}
            
* /commands/crawl/\<source_id\>

*  * method: GET

*  * content-type: application/json

*  * code: 200, 202

            +pc ~: user$ curl -X GET http://127.0.0.1:8080/commands/crawl/2
            {"http://www.bbc.co.uk/news/technology-20465982": "2"}


* /commands/fetch?url=\<url\>

*  * method: GET

*  * content-type: applicationion/json

*  * code: 200, 500

            +pc ~: user$ curl -X GET http://127.0.0.1:8080/commands/fetch?    
            url=http://www.bbc.com/news/technology-29802581
            {"keywords": ["firm", ..., "told"], "title": "Google is developing cancer and heart attack detector", "url": "http://www.bbc.com/news/technology-29802581", "text": "Google is aiming to diagnose cancers, impending heart attacks or strokes and other diseases, at a much earlier stage than is currently possible. ... On the other hand, Google's \"smart lens\" for diabetics shows promise, with Swiss firm Novartis stepping up to license the technology in July.\n\nAnd the forthcoming Android Fit platform, designed to harness data from other apps and wearables, has a good chance of success given the huge number of people using the operating system.", "images": ["http://stats.bbc.co.uk/o.gif?~RS~s~RS~News~RS~t~RS~HighWeb_Story~RS~i~RS~29802581~RS~p~RS~99113~RS~a~RS~International~RS~u~RS~/news/technology-29802581~RS~q~RS~~RS~z~RS~18~RS~", ..., "http://news.bbcimg.co.uk/media/images/78554000/jpg/_78554660_169462629.jpg"], "authors": ["Leo Kelion", "James Gallagher", "Technology Health Desk Editors"], "top_image": "http://newsimg.bbc.co.uk/media/images/67373000/jpg/_67373987_09f1654a-e583-4b5f-bfc4-f05850c6d3ce.jpg"} 
            
* /commands/update_matrices

*  * method: GET

*  * content-type: application/json

*  * code: 200, 202

            +pc ~: user$ curl -X GET http://127.0.0.1:8080/commands/update_matrices
            {"http://www.bbc.co.uk/news/technology-20465982": "2"}
            
* /commands/update_matrices/\<source_id\>

*  * method: GET

*  * content-type: application/json

*  * code: 200, 202

            +pc ~: user$ curl -X GET http://127.0.0.1:8080/commands/update_matrices/2
            {"http://www.bbc.co.uk/news/technology-20465982": "2"}
            
* /commands/rebuild_matrices

*  * method: GET

*  * content-type: application/json

*  * code: 204, 202

            +pc ~: user$ curl -X GET http://127.0.0.1:8080/commands/rebuild_matrices
