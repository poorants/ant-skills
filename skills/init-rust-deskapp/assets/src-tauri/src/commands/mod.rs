/// Example command: greet
/// Frontend calls: invoke("greet", { name: "World" })
#[tauri::command]
pub fn greet(name: &str) -> String {
    format!("Hello, {}! From Rust.", name)
}

// Add more commands below
// Each command must be registered in lib.rs invoke_handler
