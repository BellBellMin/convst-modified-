# -*- coding: utf-8 -*-

import numpy as np
from sktime.datasets import (load_UCR_UEA_dataset, 
    load_from_tsfile_to_dataframe, load_from_arff_to_dataframe
)
from sktime.datatypes._panel._convert import from_nested_to_3d_numpy

from sklearn.preprocessing import LabelEncoder

def load_sktime_dataset_split(name, normalize=True):
    """
    Load the original train and test splits of a dataset 
    from the UCR/UEA archive by name using sktime API.

    Parameters
    ----------
    name : string
        Name of the dataset to download.
    normalize : boolean, optional
        If True, time series will be z-normalized. The default is True.


    Returns
    -------
    X_train : array, shape=(n_samples_train, n_features, n_timestamps)
        Training data from the dataset specified by path.
    X_test : array, shape=(n_samples_test, n_features, n_timestamps)
        Testing data from the dataset specified by path.
    y_train : array, shape=(n_samples_train)
        Class of the training data.
    y_test : array, shape=(n_samples_test)
        Class of the testing data.
    le : LabelEncoder
        LabelEncoder object used to uniformize the class labels


    """
    #Load datasets
    X_train, y_train = load_UCR_UEA_dataset(name, return_X_y=True, split='train')
    X_test, y_test = load_UCR_UEA_dataset(name, return_X_y=True, split='test')

    #Convert pandas DataFrames to numpy arrays
    X_train = from_nested_to_3d_numpy(X_train)
    X_test = from_nested_to_3d_numpy(X_test)

    #Convert class labels to make sure they are between 0,n_classes
    le = LabelEncoder().fit(y_train)
    y_train = le.transform(y_train)
    y_test = le.transform(y_test)

    #Z-Normalize the data
    if normalize:
        X_train = (X_train - X_train.mean(axis=-1, keepdims=True)) / (
            X_train.std(axis=-1, keepdims=True) + 1e-8)
        X_test = (X_test - X_test.mean(axis=-1, keepdims=True)) / (
            X_test.std(axis=-1, keepdims=True) + 1e-8)

    return X_train, X_test, y_train, y_test, le


def load_sktime_arff_file(path, normalize=True):
    """
    Load a dataset from .arff files.

    Parameters
    ----------
    path : string
        Path to the folder containing the .ts file. Dataset name
        should be specified at the end of path to find files as
        "dataset_TRAIN.arff" and "dataset_TEST.arff"
    normalize : boolean, optional
        If True, time series will be z-normalized. The default is True.


    Returns
    -------
    X_train : array, shape=(n_samples_train, n_features, n_timestamps)
        Training data from the dataset specified by path.
    X_test : array, shape=(n_samples_test, n_features, n_timestamps)
        Testing data from the dataset specified by path.
    y_train : array, shape=(n_samples_train)
        Class of the training data.
    y_test : array, shape=(n_samples_test)
        Class of the testing data.
    le : LabelEncoder
        LabelEncoder object used to uniformize the class labels

    """
    #Load datasets
    X_train, y_train = load_from_arff_to_dataframe(path+'_TRAIN.arff')
    X_test, y_test = load_from_arff_to_dataframe(path+'_TEST.arff')

    #Convert pandas DataFrames to numpy arrays
    X_train = from_nested_to_3d_numpy(X_train)
    X_test = from_nested_to_3d_numpy(X_test)

    #Convert class labels to make sure they are between 0,n_classes
    le = LabelEncoder().fit(y_train)
    y_train = le.transform(y_train)
    y_test = le.transform(y_test)

    #Z-Normalize the data
    if normalize:
        X_train = (X_train - X_train.mean(axis=-1, keepdims=True)) / (
            X_train.std(axis=-1, keepdims=True) + 1e-8)
        X_test = (X_test - X_test.mean(axis=-1, keepdims=True)) / (
            X_test.std(axis=-1, keepdims=True) + 1e-8)

    return X_train, X_test, y_train, y_test, le


def load_sktime_arff_file_resample_id(path, rs_id, normalize=True):
    """
    Load a dataset resample from .arff files and the identifier of the 
    resample.

    Parameters
    ----------
    path : string
        Path to the folder containing the .ts file. Dataset name
        should be specified at the end of path to find files as
        "dataset_{rs_id}_TRAIN.arff" and "dataset_{rs_id}_TEST.arff"
    rs_id : int or str
        Identifier of the resample.
    normalize : boolean, optional
        If True, time series will be z-normalized. The default is True.


    Returns
    -------
    X_train : array, shape=(n_samples_train, n_features, n_timestamps)
        Training data from the dataset specified by path.
    X_test : array, shape=(n_samples_test, n_features, n_timestamps)
        Testing data from the dataset specified by path.
    y_train : array, shape=(n_samples_train)
        Class of the training data.
    y_test : array, shape=(n_samples_test)
        Class of the testing data.
    le : LabelEncoder
        LabelEncoder object used to uniformize the class labels

    """
    #Load datasets
    X_train, y_train = load_from_arff_to_dataframe(path+'_{}_TRAIN.arff'.format(rs_id))
    X_test, y_test = load_from_arff_to_dataframe(path+'_{}_TEST.arff'.format(rs_id))

    #Convert pandas DataFrames to numpy arrays
    X_train = from_nested_to_3d_numpy(X_train)
    X_test = from_nested_to_3d_numpy(X_test)

    #Convert class labels to make sure they are between 0,n_classes
    le = LabelEncoder().fit(y_train)
    y_train = le.transform(y_train)
    y_test = le.transform(y_test)

    #Z-Normalize the data
    if normalize:
        X_train = (X_train - X_train.mean(axis=-1, keepdims=True)) / (
            X_train.std(axis=-1, keepdims=True) + 1e-8)
        X_test = (X_test - X_test.mean(axis=-1, keepdims=True)) / (
            X_test.std(axis=-1, keepdims=True) + 1e-8)

    return X_train, X_test, y_train, y_test, le

def load_sktime_ts_file(path, normalize=True):
    """
    Load a dataset from .ts files

    Parameters
    ----------
    path : string
        Path to the folder containing the .ts file. Dataset name
        should be specified at the end of path to find files as
        "dataset_TRAIN.ts" and "dataset_TEST.ts"
    normalize : boolean, optional
        If True, time series will be z-normalized. The default is True.

    Returns
    -------
    X_train : array, shape=(n_samples_train, n_features, n_timestamps)
        Training data from the dataset specified by path.
    X_test : array, shape=(n_samples_test, n_features, n_timestamps)
        Testing data from the dataset specified by path.
    y_train : array, shape=(n_samples_train)
        Class of the training data.
    y_test : array, shape=(n_samples_test)
        Class of the testing data.
    le : LabelEncoder
        LabelEncoder object used to uniformize the class labels

    """
    
    #Load datasets
    X_train, y_train = load_from_tsfile_to_dataframe(path+'_TRAIN.ts')
    X_test, y_test = load_from_tsfile_to_dataframe(path+'_TEST.ts')

    #Convert pandas DataFrames to numpy arrays
    X_train = from_nested_to_3d_numpy(X_train)
    X_test = from_nested_to_3d_numpy(X_test)

    #Convert class labels to make sure they are between 0,n_classes
    le = LabelEncoder().fit(y_train)
    y_train = le.transform(y_train)
    y_test = le.transform(y_test)

    #Z-Normalize the data
    if normalize:
        X_train = (X_train - X_train.mean(axis=-1, keepdims=True)) / (
            X_train.std(axis=-1, keepdims=True) + 1e-8)
        X_test = (X_test - X_test.mean(axis=-1, keepdims=True)) / (
            X_test.std(axis=-1, keepdims=True) + 1e-8)

    return X_train, X_test, y_train, y_test, le

def load_sktime_dataset(name, normalize=True):
    """
    Load a dataset from the UCR/UEA archive by name using sktime API

    Parameters
    ----------
    name : string
        Name of the dataset to download.
    normalize : boolean, optional
        If True, time series will be z-normalized. The default is True.

    Returns
    -------
    X : array, shape=(n_samples, n_features, n_timestamps)
        Time series data from the dataset specified by name.
    y : array, shape=(n_samples)
        Class of the time series
    le : LabelEncoder
        LabelEncoder object used to uniformize the class labels
        

    """
    #Load datasets
    X, y = load_UCR_UEA_dataset(name, return_X_y=True)

    #Convert pandas DataFrames to numpy arrays
    X = from_nested_to_3d_numpy(X)

    #Convert class labels to make sure they are between 0,n_classes
    le = LabelEncoder().fit(y)
    y = le.transform(y)

    #Z-Normalize the data
    if normalize:
        X = (X - X.mean(axis=-1, keepdims=True)) / (
            X.std(axis=-1, keepdims=True) + 1e-8)

    return X, y, le


def return_all_dataset_names():
    """
    Return the names of the 112 univariate datasets of the UCR archive.

    Returns
    -------
    array, shape=(112)
        Names of the univariate UCR datasets.

    """
    return np.asarray([
            "ACSF1",
            "Adiac",
            "ArrowHead",
            "Beef",
            "BeetleFly",
            "BirdChicken",
            "BME",
            "Car",
            "CBF",
            "Chinatown",
            "ChlorineConcentration",
            "CinCECGTorso",
            "Coffee",
            "Computers",
            "CricketX",
            "CricketY",
            "CricketZ",
            "Crop",
            "DiatomSizeReduction",
            "DistalPhalanxOutlineAgeGroup",
            "DistalPhalanxOutlineCorrect",
            "DistalPhalanxTW",
            "Earthquakes",
            "ECG200",
            "ECG5000",
            "ECGFiveDays",
            "ElectricDevices",
            "EOGHorizontalSignal",
            "EOGVerticalSignal",
            "EthanolLevel",
            "FaceAll",
            "FaceFour",
            "FacesUCR",
            "FiftyWords",
            "Fish",
            "FordA",
            "FordB",
            "FreezerRegularTrain",
            "FreezerSmallTrain",
            "GunPoint",
            "GunPointAgeSpan",
            "GunPointMaleVersusFemale",
            "GunPointOldVersusYoung",
            "Ham",
            "HandOutlines",
            "Haptics",
            "Herring",
            "HouseTwenty",
            "InlineSkate",
            "InsectEPGRegularTrain",
            "InsectEPGSmallTrain",
            "InsectWingbeatSound",
            "ItalyPowerDemand",
            "LargeKitchenAppliances",
            "Lightning2",
            "Lightning7",
            "Mallat",
            "Meat",
            "MedicalImages",
            "MiddlePhalanxOutlineAgeGroup",
            "MiddlePhalanxOutlineCorrect",
            "MiddlePhalanxTW",
            "MixedShapesRegularTrain",
            "MixedShapesSmallTrain",
            "MoteStrain",
            "NonInvasiveFetalECGThorax1",
            "NonInvasiveFetalECGThorax2",
            "OliveOil",
            "OSULeaf",
            "PhalangesOutlinesCorrect",
            "Phoneme",
            "PigAirwayPressure",
            "PigArtPressure",
            "PigCVP",
            "Plane",
            "PowerCons",
            "ProximalPhalanxOutlineAgeGroup",
            "ProximalPhalanxOutlineCorrect",
            "ProximalPhalanxTW",
            "RefrigerationDevices",
            "Rock",
            "ScreenType",
            "SemgHandGenderCh2",
            "SemgHandMovementCh2",
            "SemgHandSubjectCh2",
            "ShapeletSim",
            "ShapesAll",
            "SmallKitchenAppliances",
            "SmoothSubspace",
            "SonyAIBORobotSurface1",
            "SonyAIBORobotSurface2",
            "StarLightCurves",
            "Strawberry",
            "SwedishLeaf",
            "Symbols",
            "SyntheticControl",
            "ToeSegmentation1",
            "ToeSegmentation2",
            "Trace",
            "TwoLeadECG",
            "TwoPatterns",
            "UMD",
            "UWaveGestureLibraryAll",
            "UWaveGestureLibraryX",
            "UWaveGestureLibraryY",
            "UWaveGestureLibraryZ",
            "Wafer",
            "Wine",
            "WordSynonyms",
            "Worms",
            "WormsTwoClass",
            "Yoga"])
