use std::fs::{read_dir, File};
use std::io::{Read, Write};
use std::path::Path;

use itertools::Itertools;
use lazy_static::lazy_static;
use markov;
use regex::Regex;

const BASECHAINPATH: &str = "corpi/politicalchain";

/** Initializes a base markov chain based on the files in the corpus folder. This function assumes that the files are formatted properly for the markov feeder. */
fn initialize_base_markov_chain() -> markov::Chain<String> {
    let mut base_chain: markov::Chain<String> = markov::Chain::new();
    // This assumes that the files are already formatted correctly using format_corpus_files
    for text_file in get_all_valid_texts().into_iter() {
        base_chain
            .feed_file(text_file)
            .expect("Should be able to feed files into the base markov chain.");
    }
    base_chain
        .save(BASECHAINPATH)
        .expect("Should be able to save chain");

    base_chain
}

fn load_markov_chain() -> markov::Chain<String> {
    let base_chain_result: Result<markov::Chain<String>, std::io::Error> =
        markov::Chain::load(BASECHAINPATH);
    base_chain_result.expect("Should be able to return the base chain unless there is an IO error")
}

fn extract_sentences(string_buffer: &str) -> Vec<&str> {
    lazy_static! {
        static ref SENTENCE_EXTRACT: Regex =
            Regex::new("[A-Za-z0-9'\";:,]([A-Za-z0-9\\s'\";:,]|\\.[^\\s])*[.!?]")
                .expect("Should be valid regex");
    } // Make this lazy static since this is an expensive operation and we only need it compiled once.
    SENTENCE_EXTRACT
        .find_iter(string_buffer)
        .map(|thing| thing.as_str())
        .collect()
}

/**Formats all files in the corpi/ directory into the proper form for a markov chain reader. In the bot, this would be called with a value of true*/
fn format_corpus_files(delete_old_files: bool) {
    // get the names of all the text files in the corpus directory.
    let valid_texts = get_all_valid_texts();
    for file_name in valid_texts {
        // Open each file
        let mut base_file = File::open(&file_name)
            .expect("We should be able to read these files since we *just* checked them.");

        // Make a string buffer
        let mut temp_string = String::new();
        // Read in base file into temp_string
        base_file
            .read_to_string(&mut temp_string)
            .expect("Should be able to write to string buffer.");

        temp_string = temp_string.replace("\n", " ").replace("\t", " "); // Replaces newlines and tabs with empty strings.

        // extract sentences, then return as a sentence per newline.
        temp_string = extract_sentences(&temp_string).into_iter().join("\n");

        // choose whether to save as new files or rename with a _temp suffix
        let final_name: String;
        if delete_old_files {
            final_name = file_name;
        } else {
            final_name = file_name.replace(".txt", "_temp.txt");
        }
        //Create the final file naming it final name
        let mut final_file =
            File::create(final_name).expect("Should be able to create a write only file.");
        // Write the temp_string to the final_file
        final_file
            .write(temp_string.as_bytes())
            .expect("Should be able to write to created file.");
    }
}
/** Returns a vector of strings representing the filepaths of .txt files in the corpi folder */
fn get_all_valid_texts() -> Vec<String> {
    let mut valid_texts: Vec<String> = Vec::new();
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
                        valid_texts.push(
                            path
                                .path()
                                .to_str()
                                .expect("Filename contains invalid formatting. Please make sure filenames consist of valid UTF-8 code.")
                                .to_owned()); // Decide to yield ownership since no one else can.
                            }
            }
        }
    }
    valid_texts
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
    fn test_initialize_base_chain() {
        let base_chain = initialize_base_markov_chain();
        if Path::new("corpi/politicalchain")
            .try_exists()
            .expect("some wierd error idk")
        {
            println!("chain was saved to disk!")
        } else {
            println!("chain was not saved to disk")
        }
        for i in 0..10 {
            println!("{}th string produced:", i);
            println!("{}", base_chain.generate_str());
            println!("");
        }
    }

    #[test]
    fn test_extract_sentences() {
        let test_text = "I love pie. 
        Pie is Amazing!   Truly, isn't pie the best?";
        let correct = vec![
            "I love pie.",
            "Pie is Amazing!",
            "Truly, isn't pie the best?",
        ];
        assert_eq!(correct, extract_sentences(test_text));
    }

    #[test]
    fn test_format_corpus_files() {
        format_corpus_files(true);
        assert!(true);
    }
}
