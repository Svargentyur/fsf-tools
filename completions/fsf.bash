#!/bin/bash
# FSF Tools shell completions installer
# Usage: eval "$(fsf-completions bash)" or source this file

_fsf_completion() {
    local cur prev commands
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    commands="view clean spoof randomize clone batch report presets export forge compare audit"
    
    case "$prev" in
        fsf)
            COMPREPLY=( $(compgen -W "$commands --help --version -v -q" -- "$cur") )
            return 0
            ;;
        --preset|--camera)
            local presets="iphone_15_pro iphone_14 samsung_s24_ultra samsung_s23 google_pixel_8_pro google_pixel_7 canon_eos_r5 canon_eos_r6ii nikon_z8 nikon_z6iii sony_a7iv sony_a7rv fuji_xt5 fuji_xh2 gopro_hero12 dji_mavic3 leica_q3 ricoh_griii"
            COMPREPLY=( $(compgen -W "$presets" -- "$cur") )
            return 0
            ;;
        --city)
            local cities="tokyo paris new_york london berlin rome barcelona amsterdam prague vienna istanbul dubai sydney cape_town rio moscow seoul shanghai bangkok kyoto"
            COMPREPLY=( $(compgen -W "$cities" -- "$cur") )
            return 0
            ;;
        --scene)
            COMPREPLY=( $(compgen -W "daylight_outdoor golden_hour indoor night_street portrait landscape" -- "$cur") )
            return 0
            ;;
        --locale)
            COMPREPLY=( $(compgen -W "en de jp es ru kr" -- "$cur") )
            return 0
            ;;
        --action)
            COMPREPLY=( $(compgen -W "clean randomize" -- "$cur") )
            return 0
            ;;
        -o|--output|--output-dir)
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
            ;;
    esac

    # File completion for commands that take files
    case "${COMP_WORDS[1]}" in
        view|clean|spoof|randomize|report|export|audit)
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
            ;;
        compare|clone)
            COMPREPLY=( $(compgen -f -- "$cur") )
            return 0
            ;;
        forge|batch)
            COMPREPLY=( $(compgen -f -d -- "$cur") )
            return 0
            ;;
    esac

    # Default: option completion
    case "${COMP_WORDS[1]}" in
        spoof)
            COMPREPLY=( $(compgen -W "--preset --city --make --model --software --date --author --title --artist --album --genre --year --sync-time --dry-run -o --output --help" -- "$cur") )
            ;;
        randomize)
            COMPREPLY=( $(compgen -W "--preset --city --scene --sync-time --dry-run -o --output --help" -- "$cur") )
            ;;
        forge)
            COMPREPLY=( $(compgen -W "--locale --camera --city -o --output-dir --help" -- "$cur") )
            ;;
        batch)
            COMPREPLY=( $(compgen -W "--action --preset -o --output-dir -r --recursive --help" -- "$cur") )
            ;;
        *)
            COMPREPLY=( $(compgen -W "--help" -- "$cur") )
            ;;
    esac
}

complete -F _fsf_completion fsf
