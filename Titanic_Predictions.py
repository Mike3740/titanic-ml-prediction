from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

DB_USER = "root"
DB_PASS = "Alejandro666$"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "titanic_ml"

url = URL.create(
    drivername="mysql+mysqlconnector",
    username=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)
engine = create_engine(url, pool_recycle=3600)

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    CANON_MAP = {
        "passengerid": "PassengerId",
        "survived": "Survived",
        "pclass": "Pclass",
        "name": "Name",
        "sex": "Sex",
        "age": "Age",
        "sibsp": "SibSp",
        "parch": "Parch",
        "ticket": "Ticket",
        "fare": "Fare",
        "cabin": "Cabin",
        "embarked": "Embarked",
    }
    new_cols = {}
    for c in df.columns:
        key = c.strip().lower().replace(" ", "").replace("_", "")
        new_cols[c] = CANON_MAP.get(key, c.strip())
    return df.rename(columns=new_cols)

def coerce_numeric(df, cols):
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["SibSp"] = pd.to_numeric(df["SibSp"], errors="coerce").fillna(0)
    df["Parch"] = pd.to_numeric(df["Parch"], errors="coerce").fillna(0)
    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)
    df["Title"] = df["Name"].str.extract(r",\s*([^.]*)\.", expand=False).str.strip()
    rare = df["Title"].value_counts()[lambda x: x < 10].index
    df["Title"] = df["Title"].replace(list(rare), "Rare")
    return df

def main():
    train = pd.read_sql("SELECT * FROM train_raw", engine)
    test  = pd.read_sql("SELECT * FROM test_raw",  engine)

    train = normalize_columns(train)
    test  = normalize_columns(test)

    num_cols = ["Age", "Fare", "SibSp", "Parch"]
    train = coerce_numeric(train, num_cols)
    test  = coerce_numeric(test,  num_cols)

    train = add_features(train)
    test  = add_features(test)

    num_features = ["Age", "Fare", "FamilySize"]
    cat_features = ["Pclass", "Sex", "Embarked", "Title", "IsAlone"]
    X = train[num_features + cat_features]
    y = train["Survived"].astype(int)
    X_test = test[num_features + cat_features]

    numeric_tf = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_tf = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ohe", OneHotEncoder(handle_unknown="ignore"))
    ])
    preprocess = ColumnTransformer([
        ("num", numeric_tf, num_features),
        ("cat", categorical_tf, cat_features)
    ])
    model = LogisticRegression(max_iter=300)
    pipe = Pipeline([("prep", preprocess), ("clf", model)])

    X_tr, X_va, y_tr, y_va = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    pipe.fit(X_tr, y_tr)
    pred_va = pipe.predict(X_va)
    print(f"Validation accuracy: {accuracy_score(y_va, pred_va):.3f}")

    pipe.fit(X, y)
    test_pred = pipe.predict(X_test).astype(int)

    submission = pd.DataFrame({
        "PassengerId": test["PassengerId"].values,
        "Survived": test_pred
    })

    submission.to_sql("submission_pred", engine, if_exists="replace", index=False)
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE submission_pred ADD PRIMARY KEY (PassengerId)"))
    except Exception:
        pass
    submission.to_csv("submission.csv", index=False)
    print("Saved predictions to MySQL (submission_pred) and submission.csv")

    peek = pd.read_sql("SELECT * FROM submission_pred ORDER BY PassengerId LIMIT 10", engine)
    print(peek)

if __name__ == "__main__":
    main()
