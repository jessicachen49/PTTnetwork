from pymongo import MongoClient
import jieba
import jieba.posseg as pseg

def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]  
    return stopwords

jieba.load_userdict("userdict.txt")
stopwords = stopwordslist("stopword.txt")
for group in db.finalGroup.find(): #for each group
	print("group:",group["_id"])
	for article_id in group["top30"]: #for each article in each group
		print(article_id)
		article = db.Article.find_one({"id":article_id})
		words = pseg.cut(article["Content"])
		for word,tag in words: #for each word in that article
			if word not in stopwords and len(word) > 1:
			#if word is a noun
				if tag=="nz" or tag=="nt" or tag=="ns" or tag=="nrt" or tag=="nrfg" or tag=="nr" or tag=="ng" or tag=="n":
					if db.Term.find({"term":word}).count() != 0: #if word in db
						key = db.Term.find_one({"keyword":word})
						#if it's the first time the word appears in this article 
						if db.Term.find({"term":word,"articles":article_id}).count()==0:
							db.Term.update({"term":word},{"$inc":{"df":1}}) #df = len of articles
						#if the word has appeared in this group already
						if db.Term.find({"term":word,"group.id":group["_id"]}).count()!=0: 
							if db.Term.find({"term":word,"group.id":group["_id"],"articles":article_id}).count()!=0:
								#tf+1
								db.Term.update(
						 		 	{"term": word},
						 		 	{"$inc":{"tf":1}})
							else:
								#df_group+1, push article id 
								db.Term.update(
									{"term":word,"group.id":group["_id"]},
									{"$push":{"articles":article_id},"$inc":{"group.$.df_group":1,"tf":1}})
								print("appeared",group["_id"],word,tag)
						else: #no group field
						#if word appeared in other groups
							if db.Term.find({"term":word,"articles":article_id}).count()==0:
								db.Term.update({"term":word},{"$push":{"articles":article_id}})
							db.Term.update({"term":word},{"$push":{"group":{"id":group["_id"],"df_group":1}}})
							print("new group",group["_id"],word,tag)
					else: #if word doesnt exist in db at all
						db.Term.insert({
							"date":"2018-09-19", "day_range":1,
							"term":"word",
							"articles":[article_id],
							"group":[{"id":group["_id"],"df_group":1}],
							"tf":1,"df":1})
						print("first",word,tag)
