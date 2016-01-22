# Wikipedia Category Classifier

## Summary and usage

Requried scripts:

1. "_The first scrapes the webpages and builds the dataset and a serialized classifier_ "  
These are _scraper.py_ and _model.py_ , together in one bash script *scape_and_model.sh*. _scarper.py_ reads categories from _categories.txt_, creates a directory _data_, where it stores each category's data in a separate file. _model.py_ reads from _data_, and creates a model which it saves in directory _pickledModel_.

2. "_The second should take in a new Wikipedia url as input and output the probabilities of belonging to each category_"  
   This one is _predict.py_. It takes a url from raw_input and produces output as shown below. 

The packages I used are listed in _requirements.txt_. 

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
```

## Model
I downloaded all pages in a category, as well as pages in the first-level of subcategories (going deeper was not of much help because for example for at level 2 articles in subcategories of Rare_diseases tended to be about individuals with the disease). This resulted in ~4000 articles, with a slight class imbalance, if I consider only the number of articles (as against its length). I let sklearn's class-weights deal with that. For modeling, I created a tf-idf matrix with 700 features. I selected the number of features by cross-validation on a naive-Bayes model, and selecting the number of features that resulted in the best cross-validation score. 

I trained a Logistic Regression classifier, which gave me an accuracy of ~80%. Considering that the dataset is small, and that the number of features is high, I decided to not use very complex models. Logistic Regression, SVM with a linear kernel and Random Forest - all resulted in similar values for accuracy / f1-score of close to 80%. The results for different models are in _Model Selection.ipynb_. 

The model accuracy/f1-score is not a good indicator of how good the model is in this case. This is because there's a significant intersection between categories *Rare_diseases* (907 pages) and *Congenital_disorders* (636 pages). Their intersection consists of 169 pages. Similarly, Rare_diseases(907) and Infectious_diseases(1067) have an intersection of 17 pages. All other category-pairs have <= 2 intesecting pages. This information was obtained from comparing sets of urls.  

Upon inspection of misclassified articles, I found that approximately 50% of those belong to *confusion-over-Rare_diseases-Congenital-disorders* category. The articles do belong to both categories, and we should apply more than one label when that is the case. Below is an example where the probabilities for the two categories are fairly close, and both lables are applicable.

```
$ python predict.py
Input url:  https://en.wikipedia.org/wiki/Cerebellar_hypoplasia

Probabilities:


                 Rare_diseases 52.55%
          Congenital_disorders 44.47%
               Medical_devices 00.79%
                        Cancer 00.71%
   Machine_learning_algorithms 00.53%
           Infectious_diseases 00.52%
              Organs_(anatomy) 00.43%


Predicted Category: Rare_diseases
```



## Scalability

#### Scraping
The scraping process requires only a minor change in case we scrape large amounts of data, unless Wikipedia changes its design. I iterate through categories and store a list of url-s for articles and sub-categories. Wikipedia has a about five million
articles, and storing the urls in a list will require about 5*10^6 * 90(bytes) / 10^6 = 450 MB. This is assuming each url is 50 characters long (~90 bytes in python).

However, when I finally download articles, I download for each category and write to disk. If a category turns out to be very large, or have very long articles, then I will have to split the list of urls and output separate files. 

#### Modeling
If suppose we were to use the entire Wikipedia corpus to have a category-predictor for new articles, then we will need to re-write this part of the code to use Spark with MLlib. Once this code is ready, it can easily be used on AWS after spinning up a spark-cluster with ~5 nodes, depending on time. 


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

There is a considerable overlap between the categories *Rare_diseases* and *Congenital_disorders*. 


- For each page, in addition to alpha-numeric text, I also collected the number of images (excluding tex images), number of tex images (math-equations), number of links, and number of citations. (I did not use this data for modeling.) 
Here's a table with (mean, median, sample standard deviataion) in each category:


| Category | Images	| Equations(math)  | Links| Citations |
|:---:|:-----:|:-------:|:-------:|:-------:	
Cancer | 6.5, 5.0, 9.2 | 0.0, 0.0, 0.2 | 207.9, 87.0, 328.5 | 19.6, 7.0, 36.1 
Congenital_disorders | 5.7, 4.0, 6.7 | 0.0, 0.0, 0.0 | 219.1, 139.5, 342.9 | 15.0, 6.0, 29.1 
Infectious_diseases | 6.4, 5.0, 10.6 | 0.0, 0.0, 0.0 | 266.6, 185.0, 292.8 | 23.1, 7.0, 44.0 
Machine_learning_algorithms | 5.0, 4.0, 3.0 | 18.3, 0.0, 38.6 | 86.4, 54.0, 88.3 | 7.0, 3.0, 11.0 
Medical_devices | 10.2, 6.5, 7.0 | 0.1, 0.0, 1.1 | 202.9, 177.0, 190.3 | 16.9, 7.0, 25.1 
Organs_(anatomy) | 8.6, 6.0, 13.8 | 0.0, 0.0, 0.1 | 239.4, 149.0, 321.7 | 21.2, 7.0, 34.9 
Rare_diseases | 5.0, 4.0, 2.4 | 0.0, 0.0, 0.1 | 251.6, 199.0, 209.1 | 18.4, 9.0, 29.1 


These however, are not very meaningful, because the data-set is small. We might see significant difference if we use upper level categories such as "Science" or "History".


## Next Steps
1. Updating the model to run on a cluster would be a natural next step. For this I would work with _Spark_.
2. I should come up with a better way for evaluating the model. I only need to have my own predict and scoring function, and use sklearn's probabilities. predict() would select labels based on some probability threshold (have to decide this wisely), and scoring would take into account matches between the one category label we provide in training/test data, and the list of labels from predict().
3. I can include other information that I collected: number of equations, images, citations etc for modeling.
4. Think of other information that I can scrape (from Wikipedia or perhaps other sources) to include while modeling. 
