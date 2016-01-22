# Wikipedia Category Classifier

## Model
I downloaded all pages in a category, as well as pages in the first-level of subcategories (going deeper was not of much help because for example for at level 2 articles in subcategories of Rare_diseases tended to be about individuals with the disease). This resulted in ~4000 articles, with a slight class imbalance, if I consider only the number of articles (as against its length). I let sklearn's class-weights deal with that. For modeling, I created a tf-idf matrix with 700 features. I selected the number of features by cross-validation on a naive-Bayes model, and selecting the number of features that resulted in the best cross-validation score. 

I trained a Logistic Regression classifier, which gave me an accuracy of ~80%. Considering that the dataset is small, and that the number of features is high, I decided to not use very complex models. Logistic Regression, SVM with a linear kernel and Random Forest - all resulted in similar values for accuracy / f1-score of close to 80%. The results for different models are in _Model Selection.ipynb_

## Result

The two requried scripts:

1. _The first scrapes the webpages and builds the dataset and a serialized classifier_  
These are _scraper.py_ and _model.py_ , together in one bash script *scape_and_model.sh*. _scraper.py_ runs for a longer time than _model.py_, so I kept them separate. _scarper.py_ reads categories from _categories.txt_, creates a directory _data_ within the current directory, where it stores each category's data in a separate file. _model.py_ reads from _data_, and creates a model which it saves to _pickledModel_.

2. _The second should take in a new Wikipedia url as input and output the probabilities of belonging to each category_
   This one is _predict.py_. It takes a url from raw_input and produces output as shown below. 

```
$ python predict.py
Input url:  https://en.wikipedia.org/wiki/Merge_sort

Probabilities:


   Machine_learning_algorithms 80.34%
              Organs_(anatomy) 04.88%
               Medical_devices 04.71%
                        Cancer 03.15%
          Congenital_disorders 02.76%
           Infectious_diseases 02.20%
                 Rare_diseases 01.96%



Predicted Category: Machine_learning_algorithms

$ python predict.py
Input url:  https://en.wikipedia.org/wiki/Rome                

Probabilities:


           Infectious_diseases 47.68%
                        Cancer 26.44%
              Organs_(anatomy) 12.37%
               Medical_devices 04.73%
          Congenital_disorders 04.43%
                 Rare_diseases 02.54%
   Machine_learning_algorithms 01.81%



Predicted Category: Infectious_diseases
```

## Scalability

#### Scraping
The scraping process requires only a minor change in case we scrape large amounts of data, unless Wikipedia changes its design. I iterate through categories and store a list of url-s for articles and sub-categories. Wikipedia has a about five million
articles, and storing the urls in a list will require about 5*10^6 * 90(bytes) / 10^6 = 450 MB. This is assuming each url is 50 characters long (~90 bytes in python).

However, when I finally download articles, I download for each category and write to disk. If a category turns out to be very large, or have very long articles, then I will have to split the list of urls and output separate files. 

#### Modeling
If suppose we were to use the entire Wikipedia to have a classifier for future articles say, then we will need to re-write this
part of the code to use mllib with spark. For the entire Wikipedia corpus, which is at least larger than 10 GB, we need cloud-
services such as AWS. Once the spark-code is ready, it can easily be used on AWS after spinning up about 5-10 spark-clusters.


## ~~Interesting~~ Some facts:

- Similar categories: I calculated the mean tf-idf vector for each category and calculated the cosine-similarity. The unsurprising results are tabulated below
 
cosine-similarity  | Category | Other Category 
:------:|:------------------:  | :------:
 0.8998 | Rare_diseases | Congenital_disorders |
 0.5518 | Rare_diseases | Infectious_diseases |
 0.5065 | Rare_diseases | Organs_(anatomy) |
 0.5064 | Congenital_disorders | Organs_(anatomy) |
 0.4829 | Infectious_diseases | Congenital_disorders |
 0.4776 | Infectious_diseases | Medical_devices |
 0.4759 | Medical_devices | Organs_(anatomy) |
 0.4697 | Infectious_diseases | Organs_(anatomy) |
 0.4002 | Medical_devices | Congenital_disorders |
 0.3953 | Rare_diseases | Medical_devices |
 0.2265 | Medical_devices | Machine_learning_algorithms |
 0.2082 | Organs_(anatomy) | Machine_learning_algorithms |
 0.1969 | Rare_diseases | Machine_learning_algorithms |
 0.1925 | Congenital_disorders | Machine_learning_algorithms |
 0.1767 | Infectious_diseases | Machine_learning_algorithms |

There is a considerable overlap between the categories *Rare_diseases* and *Congenital_disorders*. Rare_diseases contains 907 pages, Congenital_disorders contains 636 pages, and their intersection consists of 169 pages. 
Similarly, Rare_diseases(907) and Infectious_diseases(1067) have an intersection of 17 pages. All other category-pairs have <= 2 intesecting pages. This information is from comparing the set of urls.  


- For each page, in addition to alpha-numeric text, I also collected the number of images (excluding tex images), number of tex images (basically math-equations), number of links, and number of citations. 
Here's a table with means in each category:

| category | images	| math_eqns  | links| citations |
|:---:|:-----:|:-------:|:-------:|:-------:			
Cancer |       6.50 |       0.01 |     207.94 |      19.60 | 
Congenital_disorders |       5.66 |       0.00 |     219.13 |      14.97 | 
Infectious_diseases |       6.41 |       0.00 |     266.55 |      23.13 | 
Machine_learning_algorithms |       5.01 |      18.34 |      86.41 |       7.04 | 
Medical_devices |      10.20 |       0.10 |     202.86 |      16.92 | 
Organs_(anatomy) |       8.57 |       0.01 |     239.41 |      21.16 | 
Rare_diseases |       4.95 |       0.00 |     251.55 |      18.44 | 

These however, are not very meaningful, because the data is small and the standard deviation within each category is high. 
We might see significant difference if we use upper level categories such as "Science" or "History".

## Future Steps
1. Updating the model to run on a cluster would be a natural next step. For this I would work on _Spark_.
2. When there's a significant overlap between categories such as in case of *Rare_diseases* and *Congenital_disorders*, 
