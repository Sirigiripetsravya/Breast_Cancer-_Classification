Breast Cancer Classification Project

Overview:

This project aims to predict whether a tumor is malignant or benign using the Breast Cancer Wisconsin (Diagnostic) dataset. Machine learning techniques, specifically Support Vector Machines (SVM), were used to develop a classification model.

Dataset

The dataset used in this project is the Breast Cancer Wisconsin (Diagnostic) dataset provided by Scikit-learn.

Dataset Details:

* Number of features: 30

* Number of samples: 569

* Classes: Malignant (0) and Benign (1)

* Features Example:

    * Mean Radius

    * Mean Texture

    * Mean Perimeter

    * Mean Area

    * Mean Smoothness

* Target:

    * 0: Malignant

    * 1: Benign

Libraries and Tools Used

* Python: Programming language

* Pandas: For data manipulation

* NumPy: For numerical operations

* Matplotlib and Seaborn: For data visualization

* Scikit-learn: For machine learning model development

Steps Performed

1) Data Loading

* Loaded the dataset using sklearn.datasets.load_breast_cancer().

* Exploratory Data Analysis (EDA)

2) Visualized distributions and relationships using pair plots, scatter plots, and heatmaps.

* Checked class distribution in the dataset.

3) Data Preprocessing

* Split the dataset into training and testing sets using train_test_split().

4) Model Development

* Built an SVM classifier using sklearn.svm.SVC.

* Tuned hyperparameters for better performance.

5) Evaluation

* Evaluated the model using metrics such as accuracy, confusion matrix, and classification report.