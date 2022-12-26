pub mod utils;

fn main() {
    utils::markov::initialize_base_corpus();
    println!("Corpus initialized! Check");
}