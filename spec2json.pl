use strict;

use Data::Dumper;
use JSON;


my $ln;         # Line numer
my $mode;       # Which block we're in: c2s or s2c
my $packet;     # The current packet spec we're parsing
my $element;    # The current element in the packet spec we're parsing
my $subelement; # The current subelement (if any) we're parsing

my @packets;    # The list of packet specs

# Let's define some regex matches...

my $word = qr/\S+/;     # A string of non-whitespace
my $space = qr/\s+/;    # A string of whitespace
my $pad = qr/\s*/;      # An optional string of space

# A markdown-style bullet point
my $bullet = qr/ \* /x;
# A backtick
my $bt = qr/ \` /x;
# A number (with optional negative sign)
my $number = qr/ -? \d+ /x;
# A parentheses
my $oparen = qr/ \( /x;
my $cparen = qr/ \) /x;
# A colon separator (usually separating an item from its descripton)
my $colon = qr/ : /x;
# The rest of the content
my $rest = qr/ .* /x;


while( <> )
{
    chomp;
    $ln++;
    next unless /\S/;

    # Check headings for the packet spec sections
    if( /^#/ )
    {
        if( /server-to-client/i )
        {
            $mode = 's2c';
        }
        elsif( /client-to-server/i )
        {
            $mode = 'c2s';
        }
        else
        {
            $mode = undef;
        }
        next;
    }

    next unless defined $mode;

    if( /^\*/ )
    {
        # * 1 `SESHCORD_SV_MSG_DEL`: message was deleted
        my( $num, $name, $desc ) = /
        $bullet $space 
        ($number) $space
        $bt ($word) $bt
        $pad $colon $pad
        ($rest) $pad/x;

        die "Bad packet spec, line $ln\n" if !defined $name;

        my %packet = (
            type => $mode,
            num => $num,
            name => $name,
            desc => $desc,
            elements => []
        );
        $packet = \%packet;
        push @packets, $packet;
        $element = undef;
        $subelement = undef;

        # print( "New packet type $num $name $desc\n" );
    }
    elsif( /^  \*/ )
    {
        # * `chat` (uuid): Chat or user to send message to
        my( $name, $type, $desc ) =
        /$bullet $space $bt ($word) $bt $pad
        $oparen ($word) $cparen $pad $colon $pad ($rest)/x;
        die "Bad element spec, line $ln\n" if !defined $type;
        my %element = (
            name => $name,
            type => $type,
            desc => $desc
        );
        if( $type eq 'struct' || $type eq 'list' )
        {
            $element{children} = [];
        }

        $element = \%element;
        push @{$packet->{elements}}, $element;

        # print( "New packet element $name $type $desc\n" );
    }
    elsif( /^    \*/ )
    {
        # print( "New nested element\n" );
        my( $name, $type, $desc ) = 
        /$bullet $space $bt ($word) $bt $pad
        $oparen ($word) $cparen $pad $colon $pad ($rest)/x;
        die "Bad subelement spec, line $ln\n" if !defined $type;
        my %element = (
            name => $name,
            type => $type,
            desc => $desc
        );
        push @{$element->{children}}, \%element;
    }
    elsif( /^\s+([^*].*)/ )
    {
        # print "Continuation\n";
        $element->{desc} .= " $1";
    }
    else
    {
        die "Syntax, line $ln\n";
    }

}

my %packets;
for my $packet (@packets)
{
    $packets{$packet->{type}}->{$packet->{num}} = $packet;
}

my $json = JSON->new->allow_nonref;
print( $json->pretty->encode( \%packets ));
