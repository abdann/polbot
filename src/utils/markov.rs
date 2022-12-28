use std::fs::{read_dir, read_to_string};
use std::path::Path;

use itertools::Itertools;
use lazy_static::lazy_static;
use markov;
use regex::Regex;

/** Initializes the base chain from the original texts. */
pub fn initialize_base_chain() -> markov::Chain<String> {
    let mut base_chain: markov::Chain<String> = markov::Chain::new(); // Chose a depth of two for no reason really.
    let valid_texts = get_all_valid_texts();
    
}

// Do not take ownership here since data is simply processed here; we may want to use the original data for other purposes, therefore we don't want to invalidate it by taking ownership in the function parameter. This is why we use lifetimes.
fn extract_words(text: String) -> Vec<String> {
    lazy_static! {
        static ref WORD_EXTRACT: Regex = Regex::new(r"\w+").unwrap();
    } // This is here to make sure that the compiler only makes this regex expression *once*, since compiling regex patterns is an expensive operation.

    WORD_EXTRACT
        .find_iter(&text)
        .map(|thing| thing.as_str().to_owned())
        .collect()
}
// Take ownership here since data originates here
fn get_all_valid_texts() -> Vec<String> {
    let mut returnable: Vec<String> = Vec::new();
    let corpi_path = Path::new("corpi/");
    for thing in read_dir(corpi_path)
        .expect("Expected corpus directory. Call binary or tests from root dir.")
    {
        if let Ok(path) = thing {
            let filetype_result = path.file_type();
            if let Ok(filetype) = filetype_result {
                if filetype.is_file() && path
                    .file_name()
                    .to_str()
                    .expect("Filename contains invalid formatting. Please make sure filenames consist of valid UTF-8 code.")
                    .ends_with(".txt") {
                        returnable.push(
                            path
                                .path()
                                .to_str()
                                .expect("Filename contains invalid formatting. Please make sure filenames consist of valid UTF-8 code.")
                                .to_owned()); // Decide to yield ownership since no one else can.
                            }
            }
        }
    }
    returnable
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_all_valid_texts() {
        let correct = vec![
            "corpi/Anatomy of The State.txt".to_string(),
            "corpi/The Communist Manifesto.txt".to_string(),
            "corpi/The Conquest of Bread.txt".to_string(),
            "corpi/The Doctrine of Fascism.txt".to_string(),
        ]; // Modify this correct vector as needed. As of the writing of this unit test, these were the texts found in the corpi folder.
        let mut perhaps_correct = get_all_valid_texts();
        perhaps_correct.sort();
        assert_eq!(correct, perhaps_correct);
    }

    #[test]
    fn test_extract_words() {
        // Sham test by checking that the number of words in The Conquest of Bread is the same as the length of the vector returned from extract words
        assert_eq!(
            74460,
            extract_words(read_to_string("corpi/The Conquest of Bread.txt").unwrap()).len()
        )
    }

    #[test]
    fn test_initialize_corpus() {
        // Just goofing around
        println!("{}", initialize_base_corpus().split_whitespace().into_iter().take(50).join(" "));
        assert!(true);
    }
}
