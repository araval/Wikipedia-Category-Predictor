# Wiki Category Classifier

## Summary
I downloaded all the pages in a category, as well as pages in the first-level of subcategories. This resulted in 
___ pages, with these many in each category. 

For each page, I collected the alpha-numeric text, number of images (excluding tex images), number of tex images, 
number of links, and number of citations. 

I created a tf-idf matrix from the for modelling. I have not used the extra information on images and equations. 

## Model:
I trained a Logistic Regression classifier, which gave me an accuracy of 80%. I have not adjusted for class imbalance yet. 


## Interesting facts:

- Similar categories: I calculated the mean tf-idf vector in each category and calculated the cosine-similarity. 
 


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


- Here's a table that list the mean number of images, citations etc: 

| category | images	| math_eqns  | links| citations |
|:---:|:-----:|:-------:|:-------:|:-------:			
Cancer |       6.50 |       0.01 |     207.94 |      19.60 | 
Congenital_disorders |       5.66 |       0.00 |     219.13 |      14.97 | 
Infectious_diseases |       6.41 |       0.00 |     266.55 |      23.13 | 
Machine_learning_algorithms |       5.01 |      18.34 |      86.41 |       7.04 | 
Medical_devices |      10.20 |       0.10 |     202.86 |      16.92 | 
Organs_(anatomy) |       8.57 |       0.01 |     239.41 |      21.16 | 
Rare_diseases |       4.95 |       0.00 |     251.55 |      18.44 | 
