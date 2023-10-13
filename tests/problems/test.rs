use std::io::{self};

fn main() {
    let mut buf = String::new();
    io::stdin().read_line(&mut buf).unwrap();
    let v: i32 = buf.strip_suffix("\n").unwrap().parse().unwrap();
    println!("{}", v * 2);

}
