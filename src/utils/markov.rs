use std::fs::{read_dir, read_to_string};
use std::path::{Path, PathBuf};

use regex::{Captures, Regex};
use markov_generator::Chain;

pub fn initialize_base_corpus() {
    let mut base_chain:Chain<String> = Chain::new(2);
    let filtered_texts = get_all_valid_texts()
                            .iter()
                            .map(|file|read_to_string(file).expect("Could not read this file for some reason.")) // reading in contents of each file from the filepath
                            .map(|text|text.split_whitespace()
                                .filter(|word| !word.contains("")));
    

}

fn get_all_valid_texts() -> Vec<String> {
    let mut returnable:Vec<String> = Vec::new();
    let corpi_path = Path::new("corpi/");
    for thing in read_dir(corpi_path).expect("Expected corpus directory. Call binary or tests from root dir.") {
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
                                .to_string());
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
        let correct = vec!
            [
            "corpi/The Conquest of Bread.txt".to_string(),
            "corpi/The Communist Manifesto.txt".to_string(),
            "corpi/Anatomy of The State.txt".to_string(),
            "corpi/The Doctrine of Fascism.txt".to_string()
            ]; // Modify this correct vector as needed. As of the writing of this unit test, these were the texts found in the corpi folder.
        assert_eq!(correct, get_all_valid_texts());
    }
}