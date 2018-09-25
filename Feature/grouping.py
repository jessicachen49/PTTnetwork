from pymongo import MongoClient
db=client.test_624

Group = db.Group.find_one({"date":"2018-09-19","day_range":1})
for group in Group["overall_group_list"]:
	if db.finalGroup.find_one({"_id":group["overall_group_id"]}) == None:
		print("group",group["overall_group_id"])
		if len(group["overall_group_users"]) >20: #if the usercount of group > 15
			db.finalGroup.insert({
				"_id":group["overall_group_id"],
				"date":group["date"],
				"day_range":group["day_range"],
				"usercount":len(group["overall_group_users"]),
				"articles":[],
				"top30_len":0,
				"top30":[]
			})
		for user_id in group["overall_group_users"]: #for all users in that group
			user = db.User.find_one({"id":user_id})
			for article in user["Message"]:
				if article != "" and db.Group.find({"overall_groupArticle_list":article["ArticleId"]}) != None:
					count = db.finalGroup.find({"_id":group["overall_group_id"],"articles._id":article["ArticleId"]}).count()
					#article not in list 
					if count == 0:
						db.finalGroup.update({"_id":group["overall_group_id"]},
							{"$push":{"articles":{"_id":article["ArticleId"],"count":1}}})
					else: #article already in list
						db.finalGroup.update({"_id":group["overall_group_id"],"articles._id":article["ArticleId"]},
							{"$inc":{"articles.$.count":1}})
		db.finalGroup.update(#sort by article count
			{"_id":group["overall_group_id"]},
			{"$push":{"articles":{"$each":[],"$sort":{"count":-1}}}})
		print("group done",group["overall_group_id"])

		temp = db.finalGroup.find_one({"_id":group["overall_group_id"]})

		if db.finalGroup.find_one({"_id":group["overall_group_id"]}):		
			thirtypercent = int(len(temp["articles"])*0.33333)
			if thirtypercent < 1:
				thirtypercent=1
			for i in range(0,thirtypercent):
				print("inprogress")
				article_id = temp["articles"][i]["_id"]
				print(article_id)
				db.finalGroup.update(
					{"_id":group["overall_group_id"]},
					{"$set":{"top30_len":thirtypercent}})
				db.finalGroup.update(
					{"_id":group["overall_group_id"]},
					{"$push":{"top30":article_id}})
