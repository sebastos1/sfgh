#![no_std]
#![no_main]

use hal::{clock::ClockControl, gpio::IO, peripherals::Peripherals, prelude::*, Delay};
use esp_backtrace as _;
use esp_println::println;

#[entry]
fn main() -> ! {
    let peripherals = Peripherals::take();
    let system = peripherals.SYSTEM.split();
    let clocks = ClockControl::boot_defaults(system.clock_control).freeze();

    // Set GPIO5 as an output, and set its state high initially.
    let io = IO::new(peripherals.GPIO, peripherals.IO_MUX);
    let mut led = io.pins.gpio4.into_push_pull_output();

    led.set_high().unwrap();

    // Initialize the Delay peripheral, and use it to toggle the LED state in a
    // loop.
    let mut delay = Delay::new(&clocks);

    // top number is amount of beats in a measure, bottom number is what type of note gets 1 beat. 
    let bpm: u32 = 120;
    let whole_note: u32 = 60_000_000 / bpm;

    // no_std moment lol
    const NOTE_NAMES: [&str; 12] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    const NOTE_GAP: [u32; 12] = [3830, 3640, 3460, 3260, 3070, 2890, 2730, 2570, 2420, 2290, 2160, 2040];

    // octave + note. currently plays that one megalovania part
    let sheet: [(u32, &'static str); 68] = [
        (4, "D"), (4, "D"), (5, "D"), (4, "A"), (4, "G#"), (4, "G"), (4, "F"), (4, "D"),
        (4, "F"), (4, "G"), (4, "C"), (4, "C"), (5, "D"), (4, "A"), (4, "G#"), (4, "G"),
        (4, "F"), (4, "D"), (4, "F"), (4, "G"), (3, "B"), (3, "B"), (5, "D"), (4, "A"),
        (4, "G#"), (4, "G"), (4, "F"), (4, "D"), (4, "F"), (4, "G"), (3, "A#"), (3, "A#"),
        (5, "D"), (4, "A"), (4, "G#"), (4, "G"), (4, "F"), (4, "D"), (4, "F"), (4, "G"),
        (4, "D"), (4, "D"), (5, "D"), (4, "A"), (4, "G#"), (4, "G"), (4, "F"), (4, "D"),
        (4, "F"), (4, "G"), (4, "C"), (4, "C"), (5, "D"), (4, "A"), (4, "G#"), (4, "G"),
        (4, "F"), (4, "D"), (4, "F"), (4, "G"), (3, "B"), (3, "B"), (5, "D"), (4, "A"),
        (4, "G#"), (4, "G"), (4, "F"), (4, "D")
    ];

    loop {
        for (octave, note) in &sheet {
            let duration = 2; // all notes are half notes lol
            
            let octave_multi = if *octave > 4 {
                100 / (2 * (octave - 4))
            } else if *octave < 4 {
                100 * (2 * (4 - octave))
            } else {
                100
            };

            let i = NOTE_NAMES.iter().position(|&x| x == *note).unwrap();
            let gap = (NOTE_GAP[i] * octave_multi) / 100;

            println!("Playing a {note} ({octave}) note for a 1/{duration} beat");
            for _ in 0..whole_note / duration / gap {
                led.toggle().unwrap();
                delay.delay_us(gap);
            }
            // staccato-ish, for testing purposes
            delay.delay_ms(10u32);
        }
    }
}