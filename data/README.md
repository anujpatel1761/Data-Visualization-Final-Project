Sure! Here's a nicely formatted `README.md` version of the dataset overview:

# 🛒 Retail eCommerce Funnel Analysis Dataset

## 📄 Overview

This dataset captures user behavior on **Taobao**, one of China’s leading e-commerce platforms, over a period of **eight days**. It is specifically designed for analyzing customer journeys and **conversion funnels** in an online retail environment.

---

## 📂 File Details

- **File Name:** `user_behavior_sample_data.parquet`  
- **File Type:** Parquet File (`.parquet`)  
- **File Size:** 1.14 GB (1,225,637,388 bytes)  
- **Location:** `C:\Users\anujp\Downloads`  
- **Time Period Covered:** November 25, 2017 – December 2, 2017  
- **Total Records:** 86,953,525 rows  

---

## 📊 Dataset Schema

| Column Name   | Description                                 |
|---------------|---------------------------------------------|
| `UserID`      | Unique identifier for each user             |
| `ItemID`      | Unique identifier for each product          |
| `CategoryID`  | Identifier for the product's category       |
| `BehaviorType`| Type of user interaction (`pv`, `cart`, `fav`, `buy`) |
| `Timestamp`   | Time of interaction in UTC                  |

---

## 🔢 Unique Values

- **Users:** 987,982 unique users  
- **Items:** 3,962,559 unique products  
- **Categories:** 9,377 unique product categories  

### Behavior Types

| Behavior | Description                        |
|----------|------------------------------------|
| `pv`     | Page View – Viewing a product page |
| `cart`   | Add to Cart – Adding product to cart|
| `fav`    | Favorite – Marking a product as favorite |
| `buy`    | Purchase – Completing a transaction |

---

## 🚀 Applications

### 📈 Conversion Funnel Analysis
- Track user progression through the funnel: `pv → cart → buy`
- Calculate drop-off rates and identify funnel bottlenecks

### 🧠 Behavioral Insights
- Discover time-based user patterns
- Analyze product and category popularity

### 🏪 Real-World Use Cases
- E-commerce platform optimization  
- Marketing campaign analysis  
- Personalization and recommendation strategies

---

## 📥 Download

Offical website:
* 1) https://forum.starrocks.io/
* 2) https://forum.starrocks.io/t/retail-ecommerce-funnel-analysis-demo-with-1-million-members-and-87-million-record-dataset-using-starrocks-demo-of-starrocks/269

The dataset is available in Parquet format.  
**[Download Dataset](#)**

---

## 💻 System Requirements

To work with this dataset efficiently, it is recommended that your system meets the following specs:

- **RAM:** Minimum 16 GB  
- **Disk Space:** At least 2 GB of free space  

---

> © 2025 Retail eCommerce Funnel Analysis | Data Source: Taobao
