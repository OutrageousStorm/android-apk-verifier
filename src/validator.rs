use std::process::Command;
use std::fs;
use sha2::{Sha256, Digest};

pub struct ApkValidator;

impl ApkValidator {
    pub fn verify_signature(apk_path: &str) -> Result<String, String> {
        let output = Command::new("apksigner")
            .arg("verify")
            .arg("--verbose")
            .arg(apk_path)
            .output()
            .map_err(|e| e.to_string())?;
        
        Ok(String::from_utf8_lossy(&output.stdout).to_string())
    }
    
    pub fn get_hash(apk_path: &str) -> Result<String, String> {
        let data = fs::read(apk_path).map_err(|e| e.to_string())?;
        let mut hasher = Sha256::new();
        hasher.update(&data);
        Ok(format!("{:x}", hasher.finalize()))
    }
    
    pub fn validate(apk_path: &str) -> bool {
        match Self::verify_signature(apk_path) {
            Ok(output) => !output.contains("FAILED"),
            Err(_) => false
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        println!("Usage: {} <apk_file>", args[0]);
        return;
    }
    
    match ApkValidator::validate(&args[1]) {
        true => println!("[✓] APK signature valid"),
        false => println!("[✗] APK signature invalid")
    }
}
