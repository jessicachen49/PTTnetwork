import sys
import pandas as pd
from pymongo import MongoClient
client = MongoClient(host="140.112.107.203",port=27020,username="rootNinja",password="")
db=client.CrawlGossiping_formal

date = "2018-"
day_range = 14
Group = db.Group.find_one({"date":date,"day_range":day_range})
overall_groupArticle_list = Group["overall_groupArticle_list"]
for group in Group["overall_group_list"]:
	articles_id = []
	articles_count = []
	if db.finalGroup.find_one({"_id":group["overall_group_id"],"date":date,"day_range":day_range}) == None:
		print("group",group["overall_group_id"])
		if len(group["overall_group_users"]) > 200: #if the usercount of group > 200
			db.finalGroup.insert({
				"group_id":group["overall_group_id"],
				"date":date,
				"day_range":day_range,
				"usercount":len(group["overall_group_users"]),
				"articles":[],
				"top30_len":0,
				"top30":[]
			})
		for user_id in group["overall_group_users"]: #for all users in that group
			user = db.User.find_one({"id":user_id})
			for article in user["Message"]:
				if article != "" and "ArticleId" in article:
					if article["ArticleId"] in overall_groupArticle_list:
						print(article["ArticleId"])
						#article not in list 
						if article["ArticleId"] not in articles_id:
							articles_id.append(article["ArticleId"])
							articles_count.append(1)
						else: #article already in list
							index = articles_id.index(article["ArticleId"])
							articles_count[index] += 1
			for article in user["Article"]:

				if article != "":
					if article["art_id"] in overall_groupArticle_list:
						#article not in list 
						print(article["art_id"])
						if article["art_id"] not in articles_id:
							articles_id.append(article["art_id"])
							articles_count.append(1)
						else: #article already in list
							index = articles_id.index(article["art_id"])
							articles_count[index] += 1
		articles_dict = {"id":articles_id,"count":articles_count}
		articles_df = pd.DataFrame(articles_dict)
		articles_df = articles_df.sort_values(by=['count'])
		articles_df = articles_df.reset_index(drop=True)
			
		thirtypercent = int(len(overall_groupArticle_list)*0.33333)
		if thirtypercent < 1:
			thirtypercent=1
		top30 = articles_df.loc[0:thirtypercent]["id"].tolist()
		print("30 percent inprogress",thirtypercent)
		db.finalGroup.update(
			{"group_id":group["overall_group_id"],"date":date,"day_range":day_range},
			{
				"$set":{
					"top30_len":thirtypercent,
					"top30":top30
					}
			})
				

				
